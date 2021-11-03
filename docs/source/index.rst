py-vendor
=========
Define the vendors in a YAML config file:

.. code-block:: yaml

    # py-vendor.yml
    params:
      vendor_dir: src/my_vendors
    vendors:
      example:
        url: https://github.com/Stannislav/dummy.git
        ref: 68d5403c76fb66758c45af1d44d32d22e0c64413


Then run the vendoring process:

.. code-block:: shell

    py-vendor run --config py-vendor.yml

.. toctree::
   :maxdepth: 2
   :caption: Contents
   :hidden:

   installation
   examples

.. toctree::
   :caption: Links
   :hidden:

   GitHub <https://github.com/Stannislav/py-vendor>
   PyPI <https://pypi.org/project/py-vendor>
