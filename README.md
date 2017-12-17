# ns3-manet-compare
Manually transpilated C++ code from ns-3 manet routing example to Python.

Based on: https://www.nsnam.org/doxygen/manet-routing-compare_8cc_source.html

## Running program
Waf contains some options that automatically update the python path to find the ns3 module. To run the manet routing program, there are two ways to use waf to take care of this. One is to run a waf shell:

```sh 
$ ./waf shell
$# python work/manet_routing_compare.py [args]
```

and the other is to use the --pyrun option to waf:

```sh 
$ ./waf --pyrun work/manet_routing_compare.py [args]
```

To run a python script under the C debugger:

```sh
$ ./waf shell
$# gdb --args python work/manet_routing_compare.py [args]
```

The args are optional and have an order, as follows:
 * nSinks - int. Default: 10
 * txp - float. Default: 8.9048
 * TotalTime - int. Default: 1000
 * Nodes - int. Default: 50
 * Protocol - int. Default: 3 (means OSDV Protocol)
 * NodeSpeed - int. Default: 20 (in m/s)
 * NodePause - int. Default: 0 (in s)
 * CSVfileName - string. Default: "manet-routing.output"

## Docker support

You can use a simple Docker container, following the commands below to build and run it. Thanks for [@ryankurte](https://github.com/ryankurte/docker-ns3)

All dependencies installed for this container are listed on:  https://www.nsnam.org/wiki/Installation#Ubuntu.2FDebian.2FMint

```sh
$ docker build -t knonm/ns3-manet-compare .
$ docker run --rm -it \
    -e PROTOCOL=3 \
    -e SINKS=10 \
    -e NODE_PAUSE=100 \
    -v `pwd`/build:/usr/ns3/ns-3.26/work \
    knonm/ns3-manet-compare
```

### GUI support on OSX:

1. Install XQuartz
2. Find IP with `ifconfig en0 | grep inet | awk '$1=="inet" {print $2}'`
3. Enable IP based access with `xhost + $IP`
4. Run with  ```docker run --rm -it -v `pwd`/build:/usr/ns3/ns-3.26/work -e DISPLAY=$IP:0 -v /tmp/.X11-unix:/tmp/.X11-unix knonm/ns3-manet-compare```

For more information check out [fredrikaverpil.github.io](https://fredrikaverpil.github.io/2016/07/31/docker-for-mac-and-gui-applications/).

License
----

This repository is licensed under GNU General Public License Version 3. See *LICENSE* for further details.

**Free Software, Hell Yeah!**
