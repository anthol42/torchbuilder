import time
import random
import pandas as pd
import os
from pathlib import PurePath
from datetime import datetime
import traceback
import json

"""
This exception is raised when the result table file is locked for too long. (A time out occur).
"""


class FileLockError(Exception):
    pass


"""
# The Result Table Concept:
    The Result Table concept state that results should be stored once and be unalterable afterward.  This preserved the 
    integrity of and reproducibility of results.  Based on this definition, each result stored in a Result Table must not
    be overwritten nor deleted.  New results are only appended to the end of the table.
    To keep tract of experiments, they are indexed with the experiment name, the config file name and the hyperparameters.

    Q & A:
        Q: What happen if I redo an experiment with exact same name, config file and hyperparameters?
        A: You should not do this!  If you already run the exact same experiment, the results will be the same except is
           you have some sort of randomness.  In this situation, we strongly suggest to add a parameter representing the 
           number of time the experiment is run.  By doing so, only one experiment will run multiple time the 
           underlying experiment to produce statistics.  In fact, you should never run again an experiment that has 
           already been run since it would overwrite the results of the previous experiment, thus preventing 
           results integrity.

"""


class RecordSocket:
    """
    This is a class used to write result in its reserved spaced in the result table.  It's a unique usage class.
    This means that once the write method is called, the write method is no longer available.
    """

    def __init__(self, record: dict, metrics: list, saving_func, ignore_func):
        self.record = record
        self.save = saving_func
        self._ignore = ignore_func
        self.active = True
        self.metrics = metrics

    def get_run_id(self):
        return self.record["RunId"]

    def write(self, **kwargs):
        """
        Write results to the table
        :param kwargs: metrics to pass to the table.  Need to pass ALL the metrics at the same time.
        :return: None
        """
        if self.active:
            if set(self.metrics) != set(kwargs.keys()):
                print(set(self.metrics), set(kwargs.keys()))
                raise ValueError("Registered metrics and passed metrics are not the same!")
            for key, value in kwargs.items():
                self.record[key] = value
            self.record['LastModified'] = str(datetime.now())
            self.record["Filled"] = True
            self.save()
            self.active = False
        else:
            raise AttributeError("This record socket has already been written to.  Create an other one or create a "
                                 "new record to write again!")

    def ignore(self):
        """
        This method will remove the record socket from the table.  Call this method when an exception happen to
        avoid polluting the result table.
        Returns: None
        """
        if self.active:
            self._ignore()
            self.active = False
        else:
            raise AttributeError("This record socket has already been written to.  It is now impossible to remove "
                                 "it.")

    def __str__(self):
        s = f"{self.record['name']}<RecordSocket>\n"
        max_len = len(s)
        for metric in self.metrics:
            if self.record.get(metric) is not None:
                toAppend = f"\t{metric}: {self.record[metric]}\n"
                s += toAppend
                if len(toAppend) > max_len:
                    max_len = toAppend
            else:
                toAppend = f"\t{metric}: None\n"
                s += toAppend
                if len(toAppend) > max_len:
                    max_len = toAppend
        s += "-" * max_len
        return s


class Table:
    """
    NEW!!! Table class is now thread-proof !!!

    This class implement the Result Table concept.  The way it works is to firstly create a table with the TableBuilder
    class.  (This is done only once, see TableBuilder documentation for more info).  Once the table is created, we can
    use the Table object.  We only need to specify the path of the result table that we are using to create an instance
    of the table.  You must not create more than one instance of the same table since there would be conflicts when
    saving.  Then, we can register a result in the table.  Each line/results in a table are called records.
    It is strongly suggested to register records at the beginning of the script since it will stop the program if the
    experiment has already been done, thus preventing the run of two identical jobs.  Next, if the job is unique and no
    errors are thrown, this method will return a RecordSocket.  RecordSockets are the object your program will interact
    with.  They are directly connected to the table, but are limited to write in their allocated space.  This prevents
    data corruption.  In addition, to add a layer of security, RecordSockets can be used only once.  This means that
    once the results are written, they cannot be updated.  This improves data authenticity.  This explication was the
    basic usage of Results Tables.  When using the write method, you must pass EVERY metrics recorded in the Table at
    its construction by the TableBuilder.  Metrics are passed as keywords arguments (kwargs) to the write method and
    must not contain spelling errors.

    How to use:
        1. Create a table with TableBuilder (see documentation)
        2. Load your table at the beginning of the script and setup the error handling.  (See examples)
        3. Register the result and retrieve the RecordSocket. (At the beginning of the script)
        4. Use the RecordSocket to write the final results at the end of the experiment.  (Note that this can only be done once.)

    In addition:
        - Adding a category: use the add_category method
        - Export to excel/csv/json: use the export method that will export to a pandas dataframe.  Then, you can save it in any format.
        - Table class is thread-proof and multiprocess proof (If that even exits)

    Notes:
        Every action is saved automatically.

    Examples:
        >>>### Begining of the script ###

        >>>from resultTable import Table

        >>>import sys

        >>># This assumes that the table has already been built with two categories: CNN and Transformers

        >>># In addition, there is two metrics that are recorded in the table: crossEntropy and F1

        >>>table = Table("rtable.json")

        >>># This is for the error handling.  You must put it at the beginning of the file.

        >>>sys.excepthook = table.handle_exception(sys.excepthook)

        >>># Register the socket:

        >>>socket = table.registerRecord("CNNTest1", "CNN1.yaml", category="CNN", dataset="Huge")

        >>>### End of scripts, when experiment is done and results are collected ###

        >>>socket.write(crossEntropy=val_loss, F1=val_score)

        >>># Trying to write again to socket will result in an error:

        >>> socket.write(crossEntropy=val_loss2, F1=val_score2) # Raise exception: AttributeError

        >>># Add categories --> Usually done in the script that build the table since we usually don't add categories on the fly.

        >>>table.add_category("GAN") # Automatically saved

        >>># Export result table to csv:

        >>>table.export().to_csv("results/result_table.csv") # The export method convert the Table to pandas DataFrame.

        >>># Export result table to csv:

        >>>table.toTxt("results/CompiledResults.txt")

    """

    def __init__(self, path):
        """
        Initialize the Table class
        :param path: Path to the saved table.  (Must be a json file generated by the TableBuilder class)g.
        """

        self.path = path
        self.fd_path = f"{self.path}.lock"
        self.records = {}
        self._load_table(lock=False)
        self._record_under_modification = []  # List of list [category, run_id, state, record] --> state: save / ignore

    def _load_table(self, lock=True):
        """
        This function will refresh the in memory version of the table.  It will also lock the rtable file to avoid
        concurrent modifications.
        :param lock: Whether to lock the file or not.  If the load table is called to update the internal representation
                        of the table only, it is suggested to put it to false.  However, if the load table is called to
                        save, it is essential to lock the file.  Remember to unlock the file.  The save function already
                        handle the locking and unlocking of the file.
        Returns: None
        """
        n_try = 0
        while n_try < 10:
            time.sleep(random.random() + 0.5)
            n_try += 1
            if lock:
                try:
                    self.fd = open(self.fd_path, "x")
                    break
                except FileExistsError:
                    continue
            else:
                if not os.path.exists(self.fd_path):
                    break

        if n_try == 10:
            raise FileLockError(f"Maximum number of retry to read the rtable file.  MAX_RETRY: {n_try}")
            # Lock the file until saving to avoid conflict between the ram and stored version.

        with open(self.path, 'r') as file:
            load_dict = json.load(file)

        self.allow_update = load_dict['metadata']['allow_update']
        self.name = load_dict['metadata']['name']
        self.timeCreated = load_dict['metadata']['timeCreated']
        self.format = load_dict['metadata']['format']
        self.round_decimal = load_dict['preferences']['round_decimal']

        self.metrics = load_dict['metrics']
        self.records = load_dict["records"]

        if len(self.records.keys()) == 0:
            self.records["defaultCategory"] = []

    def format_hyper(self, hyperparameters: dict) -> str:
        hyper_str = [f"{key}:{value}" for key, value in hyperparameters.items()]
        return "\n".join(hyper_str)

    def registerRecord(self, experiment_name: str, config_file_name: str, category: str = None, **hyperparameters):
        """
        Register a place in the table where to store metrics from experiment.
        :param experiment_name: Name of the experiment
        :param config_file_name: Name of the config file
        :param category: The category where to put it, if no category is provided, it will store it in the default category
        :param hyperparameters: Hyperparameters are passed as kwargs.  Since we use a config file, for most
                                cases, it is usually empty.  It is possible to add as kwargs hyperparameters
                                that we plan to change a lot to try different combination.  This way, we don't have to
                                make a new config file with almost every thing identical to other s except one
                                hyperparameter.
        :return: TableSocket, the object with which it is possible to write results to the Table.
        """
        self._load_table(lock=True)
        if category and category not in self.records.keys():
            self._unlock()
            raise ValueError("Invalid category name")
        if not category:
            category = "defaultCategory"
        hyper_format = self.format_hyper(hyperparameters)
        record_state = 'CREATED'
        record_idx = None
        # Verify if experiment already exist to avoid creating a duplicate
        for i, record in enumerate(self.records[category]):
            if record['name'] == experiment_name and \
                    record['hyperparameters'] == hyper_format and \
                    record['config'] == config_file_name and record["Filled"]:
                if self.allow_update:
                    record_state = 'UPDATE'
                    record_idx = i
                    break
                else:
                    self._unlock()
                    raise ValueError(f"Experiment already exits! RunId: {record['RunId']}")
            elif record['name'] == experiment_name and \
                    record['hyperparameters'] == hyper_format and \
                    record['config'] == config_file_name and not record["Filled"]:
                record_idx = i
                record_state = 'FILL'
                break
        if record_state == 'UPDATE':
            old_record_state = self.records[category][record_idx]['status']
            self.records[category][record_idx]['status'] = record_state
            run_id = self.records[category][record_idx]["RunId"]

            def ignore():
                index_list = [item["RunId"] for item in self.records[category]]
                idx = index_list.index(run_id)
                self.records[category][idx]["status"] = old_record_state

                # Remove it from state under modification
                index_list = [item[1] for item in self._record_under_modification]
                idx = index_list.index(run_id)
                self._record_under_modification[idx][2] = "ignore"
                self._save()
        elif record_state == 'FILL':
            old_record_state = self.records[category][record_idx]['status']
            run_id = self.records[category][record_idx]["RunId"]

            def ignore():
                index_list = [item["RunId"] for item in self.records[category]]
                idx = index_list.index(run_id)
                self.records[category][idx]["status"] = old_record_state

                # Remove it from state under modification
                index_list = [item[1] for item in self._record_under_modification]
                idx = index_list.index(run_id)
                self._record_under_modification[idx][2] = "ignore"
                self._save()
        else:
            record_idx = len(self.records[category])
            run_id = self.create_run_id()
            # Create a new record socket
            self.records[category].append({
                "RunId": run_id,
                "name": experiment_name,
                "config": config_file_name,
                "hyperparameters": hyper_format,
                "status": record_state,
                "LastModified": str(datetime.now()),
                "Filled": False
            })
            for metric in self.metrics:
                self.records[category][record_idx][metric] = None

            def ignore():
                index_list = [item["RunId"] for item in self.records[category]]
                idx = index_list.index(run_id)
                del self.records[category][idx]

                # Remove it from state under modification
                index_list = [item[1] for item in self._record_under_modification]
                idx = index_list.index(run_id)
                self._record_under_modification[idx][2] = "ignore"
                self._save()
        self._record_under_modification.append([category, run_id, "save", self.records[category][record_idx].copy()])
        socket = RecordSocket(self._record_under_modification[-1][-1], self.metrics, self._save, ignore)
        # File is already locked, no need to load the table again when saving.
        self._save(fileIsLock=True)
        return socket

    def create_run_id(self):
        max_id = 0
        for cat in self.records.values():
            for record in cat:
                if record["RunId"] > max_id:
                    max_id = record["RunId"]

        return max_id + 1

    def add_category(self, category_name: str):
        """
        Add a category to the table.  Usually used in the table builder scripts
        :param category_name: The name of the category to add
        :return: None
        """
        if category_name in self.records.keys():
            raise ValueError("Category already exist.")
        self.records[category_name] = []
        self._save()

    def _save(self, fileIsLock=False):
        """
        Internal function.  YOU MUST NOT USE IT!!!!
        :return:
        """
        # Save record to another variable since we are going to overwrite them with the load_table method.
        internal_record = self.records.copy()
        # If the file is locked, the data in the ram is the same as it is in the file, so no need to load it again.
        if not fileIsLock:
            self._load_table()
        table = {
            "metadata": {
                "name": self.name,
                "timeCreated": self.timeCreated,
                "format": self.format,
                "allow_update": self.allow_update
            },
            "preferences": {
                "round_decimal": self.round_decimal
            },
            "metrics": self.metrics,
            "records": self.records
        }
        # Add categories:
        new_categories = list(set(internal_record.keys()) - set(table["records"].keys()))
        if len(new_categories) > 0:
            for cat in new_categories:
                table["records"][cat] = []

        # Add or modify records in the table
        for cat, run_id, state, record in self._record_under_modification:
            # Search for specific record in stored table (On disk)
            stored_record_idx = [item["RunId"] for item in self.records[cat]]
            try:
                stored_idx = stored_record_idx.index(run_id)  # If record exist in stored table
            except ValueError:
                stored_idx = -1  # If record doesn't exist in stored table

            if state == "save":
                if stored_idx == -1:
                    table["records"][cat].append(record)
                else:
                    table["records"][cat][stored_idx] = record
            else:  # state is ignore, we need to remove it from the table
                if stored_idx > -1:
                    del table["records"][cat][stored_idx]

                # If stored idx is equal to -1, this means that the record wasn't found in the stored table.  In this
                # case, we do not have to do nothing.
        try:
            with open(f"{self.path}.tmp", 'w') as file:
                json.dump(table, file)
        except TypeError:
            traceback.print_exc()
            os.remove(f"{self.path}.tmp")
            os.close(self.fd)
            os.unlink(self.fd_path)
            exit(1)
        with open(f"{self.path}", 'w') as file:
            json.dump(table, file)
        try:
            os.remove(f"{self.path}.tmp")
        except:
            pass

        self._unlock()
        # self.fd.close()
        # os.unlink(self.fd_path)

    def _unlock(self):
        """
        This method unlock the config file.
        """
        self.fd.close()
        os.unlink(self.fd_path)

    def _ignore_all(self):
        """
        This method ignore all the records that haven't been filled yet.  (It removes them from the table.)
        :return: None
        """
        self._load_table(lock=False)
        for rec in self._record_under_modification:
            category = rec[0]
            run_id = rec[1]
            ram_record_idx = [item["RunId"] for item in self.records[category]]
            try:
                ram_idx = ram_record_idx.index(run_id)
                if not self.records[category][ram_idx]["Filled"]:
                    rec[2] = "ignore"
            except ValueError:
                # If a value error happens, it means that the record has already been ignored, so we do not ignore it
                # again.
                pass
        self._save()

    def handle_exception(self, excepthook):
        """
        This method is made to handle exception.  In a case where record have been registered, but not written to, and
        an exception happen, to avoid having unfilled record in the result table (polluting the result table), set the
        sys.except hook with the return callback of this method.  The callback will clean every unfilled record when an
        exception happen.

        :param excepthook: the value of sys.excepthook (see examples for more details)
        :return: callback
        """

        def _handle_exception(t, value, tb):
            self._ignore_all()
            excepthook(t, value, tb)

        return _handle_exception

    def export(self) -> pd.DataFrame:
        """
        Export to pandas DataFrame
        :return: pandas.DataFrame
        """
        columns = ["RunId", "Category", "Experiment", "Hyperparameters", "Configuration"] + self.metrics + ["Status",
                                                                                                            "Last Modified"]
        data = []
        for categoryName, categoryContent in self.records.items():
            for record in categoryContent:
                rec = [record["RunId"], categoryName, record["name"], record["hyperparameters"], record["config"]]
                for metric_name in self.metrics:
                    rec.append(record[metric_name])
                rec += [record["status"], record["LastModified"]]
                data.append(rec)

        df = pd.DataFrame(data=data, columns=columns)
        df = df.set_index(df["RunId"])
        df.index.name = 'Run Id'
        return df

    def __str__(self):
        pd.set_option('display.max_rows', 500)
        pd.set_option('display.max_columns', 500)
        pd.set_option('display.width', 1000)
        df = self.export()

        def formtHyper(x):
            x_list = x.split("\n")
            if len(x_list) > 3:
                return ", ".join(x_list[:3]) + ", ..."
            else:
                return ", ".join(x_list)

        df["Hyperparameters"] = df["Hyperparameters"].apply(formtHyper)
        df["Category"] = df["Category"].apply(lambda x: "" if x == "defaultCategory" else x)
        df = df.drop(columns=["RunId"])
        df = df.groupby("Category", group_keys=True).apply(lambda x: x).drop(columns=["Category"])
        return str(df)

    def toTxt(self, filepath="results/CompiledResults.txt"):
        """
        Save file in a visually nice looking text format (lossy).  It is lossy since it might round numbers and may not
        display everything to make results interpretable in a glance. If you want more precision and make a complete
        anlysis, consider the export method.
        :param filepath: Filepath to save file
        :return: None
        """
        with open(filepath, "w") as file:
            file.write(str(self))


class TableBuilder:
    """
    This class can create a result table of the class Table.  This class must be in a script that will be run only
    one time to create the table.  Every future attempts will result in exception since you cannot create a new table
    to override the old one.  (Table are designed to be unalterable.  See Table's documentation for more info.)

    How to use:
      1. Initiate a TableBuilder object with desired options (The metrics you want to include* and the path where to
         save the table**)
      2. Call the build method of the builder only once to build the table. The method will return the created Table.
      3. Add categories.

      * You need to pass every metrics you want to include in this table since you cannot add any later.  Note that
        every metric you add will be require with every records.  (Empty cell are not allowed)
      ** Note that table are saved automatically so pick a location that can handle a lot of read/write.

    Examples:
        >>># Build a table with F1 and crossEntropy as metrics values.  (Same as the Table's example.

        >>>table = TableBuilder(["F1", "crossEntropy"], PurePath("rtable.json")).build() # We save the table to path: rtable.json

        >>># Add categories to the table.

        >>>table.add_category("CNN")

        >>>table.add_category("Transformer")
    """

    def __init__(self, metrics_names: list, path: PurePath, round_decimal: int = 3, allow_update=False):
        """
        Create a new TableBuilder, an object made to create new resultTables.
        :param metrics_names: A list containing strings that correspond to the names of the metrics to include.
        :param path: The path(with the name) to the Table to be created.
                     It must be a location that handle a lot of read/write
        :param round_decimal: The number of precision decimal to keep when rounding the results
        :param allow_update: Whether to make the records updatable or unalterable.  It is strongly suggested to never
               allow updates.
        """
        self.metrics = metrics_names
        self.path = path
        self.name = path.name
        self.round_decimal = round_decimal
        self.allow_update = allow_update
        if not os.path.exists(path.parent):
            os.makedirs(path.parent)
        if os.path.exists(self.path):
            raise FileExistsError("The table has already been created!")

    def build(self) -> Table:
        """
        Builds the table, save it and return it.
        :return: The newly created Table
        """
        if os.path.exists(self.path):
            raise FileExistsError("The table has already been built!")
        table = {
            "metadata": {
                "name": self.name,
                "timeCreated": str(datetime.now()),
                "format": "JSON",
                "allow_update": self.allow_update
            },
            "preferences": {
                "round_decimal": self.round_decimal
            },
            "metrics": self.metrics,
            "records": {}
        }
        with open(self.path, 'w') as file:
            json.dump(table, file)
        return Table(path=self.path)


if __name__ == "__main__":
    ### To make the example runnable more than once, I reset the table at every run.  Do not do this in experimentation!
    import sys
    from color import TraceBackColor, Color

    sys.excepthook = TraceBackColor(Color(203))

    ## In table builder script (Should be in an auxiliary file) ##
    if os.path.exists("rtable.json"):
        os.remove("rtable.json")
    table = TableBuilder(["F1", "crossEntropy"], PurePath("rtable.json")).build()

    table.add_category("CNN")
    table.add_category("Transformer")
    ## End of builder script ##

    ## Example of what will happen in an experiment script ##

    table = Table("rtable.json")

    # Exception handling
    sys.excepthook = table.handle_exception(sys.excepthook)

    socket1 = table.registerRecord("CNNTest1", "CNN1.yaml", category="CNN", dataset="Huge")
    socket2 = table.registerRecord("CNNTest2", "CNN1.yaml", category="CNN", dataset="Huge")
    socket1.write(crossEntropy=3.0, F1=0.98)
    print(10 / 0)
    # socket.ignore()
    # End of script:
    # print(10/0)

    # Export to csv
    table.toTxt("result_table.txt")