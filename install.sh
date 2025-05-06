echo "installing TorchBuilder..."

cd ..
cp -r torchbuilder ~
sudo mkdir -p /usr/local/bin
sudo cp torchbuilder/torchbuilder.sh /usr/local/bin/torchbuilder
sudo chmod +x /usr/local/bin/torchbuilder

rm -rf ~/torchbuilder/.git

echo "installation done!"
