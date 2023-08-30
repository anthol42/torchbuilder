
echo "building virtual env named venv with $1"

module load python/$1

virtualenv --no-download venv

source venv/bin/activate

pip install --no-index --upgrade pip

pip install -r requirement.txt --no-index

echo ""

echo "Done!"

