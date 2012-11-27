

# ensure that apt update is run before any packages are installed
class apt {
  exec { "apt-update":
    command => "/usr/bin/apt-get update"
  }

  # Ensure apt-get update has been run before installing any packages
  Exec["apt-update"] -> Package <| |>

}


include apt



exec { "add-apt":
  command => "/usr/bin/add-apt-repository -y ppa:mapnik/nightly-2.0 && /usr/bin/apt-get update",
  subscribe => Package["python-software-properties"]
}



package { "git-core":
    ensure => "latest"
}

package { "subversion":
    ensure => "latest"
}

package { "mercurial":
    ensure => "latest"
}

package { "csstidy":
    ensure => "latest"
}


package { "vim":
    ensure => "latest"
}


package { "python-psycopg2":
    ensure => "latest"
}

package { "python-virtualenv":
    ensure => "latest"
}

package { "python-dev":
    ensure => "latest"
}


package { "build-essential":
    ensure => "installed"

}


package { "libmapnik":
    ensure => "installed",
    subscribe => Exec['add-apt']
}


package { "mapnik-utils":
    ensure => "installed",
    subscribe => Exec['add-apt']
}


package { "python-mapnik":
    ensure => "latest",
    subscribe => Exec['add-apt']
}

package { "python-kombu":
    ensure => "installed"
}


package { "python-software-properties":
    ensure => "installed"

}

class { "postgresql::server": version => "9.1",
    listen_addresses => 'localhost',
    max_connections => 100,
    shared_buffers => '24MB',
}

postgresql::database { "debris":
  owner => "vagrant",
}


python::venv::isolate { "/usr/local/venv/debris":
  requirements => "/vagrant/requirements.txt",
  subscribe => Package['build-essential'],
}

