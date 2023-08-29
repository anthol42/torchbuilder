
echo "building virtual env named venv with python $1"

module load python/$1

virtualenv --no-download venv

source venv/bin/activate

pip install --no-index --upgrade pip

pip install -r requirements.txt --no-index

echo ""

echo "Done!"

