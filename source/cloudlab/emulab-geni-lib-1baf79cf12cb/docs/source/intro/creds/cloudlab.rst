.. Copyright (c) 2016  Barnstormer Softworks, Ltd.

.. raw:: latex

  \newpage

Getting Credentials from the CloudLab Portal
============================================

CloudLab only provides your x509 certificate from the web interface.  You will
have to provide your own SSH public key for use with `geni-lib` when you set
up your context for using reserved resources.

* Log in to the `CloudLab Portal <https://www.cloudlab.us/login.php>`_.
* From the **Actions** dropdown at the top of the interface, select the
  **Download Credentials** option
* Save this text (either via copy/paste or **Save As...** in your brower) to
  a file called ``cloudlab.pem`` for use when creating your context.
