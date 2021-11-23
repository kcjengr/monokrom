# MonoKrom Virtual Control Panel

Monochrome style VCPs for LinuxCNC controlled Lathes, Mills and Plasma cutters.

*Main page*
![](docs/images/Web19201.png)

*Main page 1024pxx768px*
![](docs/images/screenshot.png)


*Plasma Settigns page*
![](docs/images/screenshot-1.png)

## Installation

If you have not already done so, install the [QtPyVCP software dependencies](http://www.qtpyvcp.com/install/prerequisites.html#software-dependencies)

Install QtPyVCP

`python3 -m pip install qtpyvcp`

Install MonoKrom (includes lathe, mill and plasma VCPs)

`python3 -m pip install git+https://github.com/kurtjacobson/monokrom-vcp`


The current Plasma development version which is under active development is located at:
https://github.com/joco-nz/monokrom-vcp

If the Plasma UI is of interest then the recommended install is:

`
cd <directory where you want to have the git cloned repo>
git clone https://github.com/joco-nz/monokrom-vcp
cd monokrom-vcp
python3 -m pip install -e .`

This will create an editable installe of Monokrom.  To update to the latest development state cd into monokrom-vcp and perform

`git pull`


To install the MonoKrom LinuxCNC sim configs run:

`monokrom --install-sim`


## Acknowledgements

Designed by: [@pinder](https://forum.linuxcnc.org/cb-profile/pinder)  
Forum Thread: [forum.linuxcnc.org/qtpyvcp/40082](https://forum.linuxcnc.org/qtpyvcp/40082)
