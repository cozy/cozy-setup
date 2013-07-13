$provision = <<SCRIPT
sudo apt-get --yes --force-yes install build-essential git

exe="/usr/local/bin/cozy-monitor"

appsToStart=("data-system" "home" "proxy")

echo "STARTING MAIN APPS"
for app in ${appsToStart[@]}
do
    $exe start $app
done

echo "CURRENT COZY STATUS"
$exe status
SCRIPT

Vagrant.configure("2") do |config|

  # Every Vagrant virtual environment requires a box to build off of.
  config.vm.box = "cozycloud-dev-latest"

  # The url from where the 'config.vm.box' box will be fetched if it
  # doesn't already exist on the user's system.
  config.vm.box_url = "http://files.cozycloud.cc/cozycloud-dev-latest.box"

  # Assign this VM to a host-only network IP, allowing you to access it
  # via the IP. Host-only networks can talk to the host machine as well as
  # any other machines on the same network, but cannot be accessed (through this
  # network interface) by any external networks.
  config.vm.network :private_network, ip: "192.168.50.4"
  #config.vm.network :public_network

  # Forward a port from the guest to the host, which allows for outside
  # computers to access the VM
  config.vm.network :forwarded_port, guest: 9101, host: 9101 # Cozy Data System
  config.vm.network :forwarded_port, guest: 9102, host: 9102 # Cozy Data Indexer
  config.vm.network :forwarded_port, guest: 9104, host: 9104 # Cozy Proxy
  config.vm.network :forwarded_port, guest: 9105, host: 9105 # Realtime socket
  config.vm.network :forwarded_port, guest: 5984, host: 5984 # CouchDB
  config.vm.network :forwarded_port, guest: 9099, host: 9099 # Cozy Log Reader

  config.vm.synced_folder ".", "/vagrant"# , :nfs => true

  config.vm.provider :virtualbox do |vb|
    vb.customize ["modifyvm", :id, "--memory", "512"]
  end

  config.vm.provision :shell, :inline => $provision
end
