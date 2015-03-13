Vagrant.configure("2") do |config|

  # Base box for Cozy development environment.
  config.vm.box = "cozycloud/cozy-dev"

  # Assign this VM to a host-only network IP, allowing you to access it
  # via the IP. Host-only networks can talk to the host machine as well as
  # any other machines on the same network, but cannot be accessed (through this
  # network interface) by any external networks.
  #config.vm.network :private_network, ip: "192.168.50.4"
  #config.vm.network :public_network

  # Forward a port from the guest to the host, which allows for outside
  # computers to access the VM
  config.vm.network :forwarded_port, guest: 9101, host: 9101 # Cozy Data System
  config.vm.network :forwarded_port, guest: 9002, host: 9002 # Cozy Controller
  config.vm.network :forwarded_port, guest: 9102, host: 9102 # Cozy Data Indexer
  config.vm.network :forwarded_port, guest: 9104, host: 9104 # Cozy Proxy
  config.vm.network :forwarded_port, guest: 9105, host: 9105 # Realtime socket
  config.vm.network :forwarded_port, guest: 5984, host: 5984 # CouchDB

  config.vm.synced_folder ".", "/vagrant"# , :nfs => true

  config.vm.provider :virtualbox do |vb|
    vb.customize ["modifyvm", :id, "--memory", "1024"]
  end
end
