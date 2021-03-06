==========
Selfingsim
==========

Selfingsim is a forward-in-time population genetic simulator for studying
evolution of partially selfing organisms.
It was developed for and used in
"Bayesian co-estimation of selfing rate and locus-specific mutation
rates for a partially selfing population"
(Redelings *et al.* 2015, `link`_).

Characteristics of selfingsim are:

- constant population size
- inter-locus (but not intra-locus) recombination
- three different mating schemes (pure hermaproditism, androdioecy, and gynodioecy)
- the infinitie-alleles model of mutation

Installation
============

Selfingsim depends on other projects:

- Python (required; version 2.7, or version 3.0+)
- pip (required; comes with recent verions of Python): a tool to install python packages
- `simuPOP`_ (required): a framework for forward-in-time population genetic simulations
- `nose`_ (optional): a testing framework for python

After installing Python and simuPOP following their instructions,
selfingsim can be obtained from this `download link`_.
Once unpacked the downloaded file, :code:`pip install <the unpacked directory>`
installs selfingsim.

Usage
=====

After installation, selfingsim is accessible from command line terminals as
`selfingsim <command> [options]`.
Several commands are available to facilitate conducting simulations,
computing a few simple statistics, and formatting simulation results
suitable for analyzing with 3rd party softwares.

Running simulations (simulate)
------------------------------

To start a simulation, run:

    selfingsim simulate <input file>

where input file should contain all settings pertinent to a simulation,
from the mating model to population size, and the file must be in JSON format.
An example file with annotation can be found under examples directory.
Note the annotation (anything after "//") must not be in the actual
input file.

Taking subsets of organisms (`sample`)
--------------------------------------

After simulation is finished, a data file containing genotype of
all organisms at the end of simulations is created in the same directory
as the input file.
Depending on the setting, this file may also contains genotypes of
all organisms at some intermediate time.

As most of statistical methods work with samples rather than a population,
it is often necessary to sample subsets of organism from simulation results.
Selfingsim provides a simple way to sample organisms:
    selfingsim sample <data file> <generation> <size>
Parameters are:
1. data file: a file storing simulation results (after `selfingsim simulate`).
2. generation: from which generation samples should be taken.
3. size: sample size

The result is stored in a file identically named to <data file>.

Calculating heterozygosities and F_is (`selfingsim analyze`)
------------------------------------------------------------

Once a sample is taken, simple analysis can be performed on the dataset by:

    selfingsim analyze <sample file>

This command reports per-locus observed and expected heterozygosities under
Hardy-Weinberg equilibrium, F_is, number of distinct alleles.
It also reports average of these quantities over all loci.

Converting file formats (`selfingsim nexus` etc)
------------------------------------------------

Thrid-party inference software often requires dataset in a specific format.
We provide conversion to several formats.
Currently supported format and known programs to work with each format are:

======= ====== ====== ==========================
command format suffix known program to work with
======= ====== ====== ==========================
phase   PHASE  .phase `bali-phy`_
rmes    RMES   .rmes  `RMES`_
nexus   NEXUS  .nex   `GDA`_
======= ====== ====== ==========================

Conversion can be performed from the sample file as:

    selfingsim <phase/rmes/nexus> <sample file>

The result file is identically name to the sample file except file extension
is replaced by either ".phase", ".rmes", or ".nex".
Note that these conversion commands generate new files with platform-native
new line character by default.
For example, if running "rmes" commands on Linux creates a file with "\n".
However, RMES and GDA are known to only work with Windows-native new line
characters in their respective input file.
To force Windows' new line character on any platform, add "-w" to the command:

    selfingsim <phase/rmes/nexus> -w <sample file>


.. _link: http://www.example.com
.. _download link: https://github.com/skumagai/selfingsim/archive/master.zip
.. _here:
.. _simuPOP: http://simupop.sourceforge.net
.. _nose: https://github.com/nose-devs/nose
.. _bali-phy: http://www.bali-phy.org/
.. _gda: http://hydrodictyon.eeb.uconn.edu/people/plewis/software.php
.. _rmes: http://www.cefe.cnrs.fr/index.php/fr/recherche/accueil-dpt-ecologie-evolutive/genetique-et-ecologie-evolutive/800-gge/gge-chercheurs/196-patrice-david
