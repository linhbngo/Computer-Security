# Copyright (c) 2014-2016  Barnstormer Softworks, Ltd.

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from __future__ import absolute_import, print_function

import datetime
import json
import multiprocessing as MP
import os
import os.path
import tempfile
import time
import traceback as tb
import zipfile

from .aggregate.apis import ListResourcesError, DeleteSliverError

def _getdefault (obj, attr, default):
  if hasattr(obj, attr):
    return obj[attr]
  else:
    return default

def checkavailrawpc (context, am):
  """Returns a list of node objects representing available raw PCs at the
given aggregate."""

  avail = []
  ad = am.listresources(context)
  for node in ad.nodes:
    if node.exclusive and node.available:
      if "raw-pc" in node.sliver_types:
        avail.append(node)
  return avail


def _corelogininfo (manifest):
  from .rspec.vtsmanifest import Manifest as VTSM
  from .rspec.pgmanifest import Manifest as PGM

  linfo = []
  if isinstance(manifest, PGM):
    for node in manifest.nodes:
      linfo.extend([(node.client_id, x.username, x.hostname, x.port) for x in node.logins])
  elif isinstance(manifest, VTSM):
    for container in manifest.containers:
      linfo.extend([(container.client_id, x.username, x.hostname, x.port) for x in container.logins])
  return linfo


def printlogininfo (context = None, am = None, slice = None, manifest = None):
  """Prints out host login info in the format:
::
  [client_id][username] hostname:port

If a manifest object is provided the information will be mined from this data,
otherwise you must supply a context, slice, and am and a manifest will be
requested from the given aggregate."""

  if not manifest:
    manifest = am.listresources(context, slice)

  info = _corelogininfo(manifest)
  for line in info:
    print("[%s][%s] %s: %d" % (line[0], line[1], line[2], line[3]))


# You can't put very much information in a queue before you hang your OS
# trying to write to the pipe, so we only write the paths and then load
# them again on the backside
def _mp_get_manifest (context, site, slc, q):
  try:
    # Don't use geni.tempfile here - we don't want them deleted when the child process ends
    # TODO: tempfiles should get deleted when the parent process picks them back up
    mf = site.listresources(context, slc)
    tf = tempfile.NamedTemporaryFile(delete=False)
    tf.write(mf.text)
    path = tf.name
    tf.close()
    q.put((site.name, slc, path))
  except ListResourcesError:
    q.put((site.name, slc, None))
  except Exception:
    tb.print_exc()
    q.put((site.name, slc, None))

def getManifests (context, ams, slices):
  """Returns a two-level dictionary of the form:
::
  {slice_name : { site_object : manifest_object, ... }, ...}

Containing the manifests for all provided slices at all the provided
sites.  Requests are made in parallel and the function blocks until the
slowest site returns (or times out)."""

  sitemap = {}
  for am in ams:
    sitemap[am.name] = am

  q = MP.Queue()
  for site in ams:
    for slc in slices:
      p = MP.Process(target=_mp_get_manifest, args=(context, site, slc, q))
      p.start()

  while MP.active_children():
    time.sleep(0.5)

  d = {}
  while not q.empty():
    (site,slc,mpath) = q.get()

    if mpath:
      am = sitemap[site]
      data = open(mpath).read()
      mf = am.amtype.parseManifest(data)
      d.setdefault(slc, {})[sitemap[site]] = mf

  return d


def _mp_get_advertisement (context, site, q):
  try:
    ad = site.listresources(context)
    q.put((site.name, ad))
  except Exception:
    q.put((site.name, None))

def getAdvertisements (context, ams):
  """Returns a dictionary of the form:
::
  { site_object : advertisement_object, ...}

Containing the advertisements for all the requested aggregates.  Requests
are made in parallel and the function blocks until the slowest site
returns (or times out).

.. warning::
  Particularly large advertisements may break the shared memory queue
  used by this function."""


  q = MP.Queue()
  for site in ams:
    p = MP.Process(target=_mp_get_advertisement, args=(context, site, q))
    p.start()

  while MP.active_children():
    time.sleep(0.5)

  d = {}
  while not q.empty():
    (site,ad) = q.get()
    d[site] = ad

  return d


def deleteSliverExists(am, context, slice):
  """Attempts to delete all slivers for the given slice at the given AM, suppressing all returned errors."""
  try:
    am.deletesliver(context, slice)
  except DeleteSliverError:
    pass

def builddot (manifests):
  """Constructs a dotfile of the topology described in the passed in manifest list and returns it as a string."""
  # pylint: disable=too-many-branches

  from .rspec import vtsmanifest as VTSM
  from .rspec.pgmanifest import Manifest as PGM

  dot_data = []
  dda = dot_data.append # Save a lot of typing

  dda("digraph {")

  for manifest in manifests:
    if isinstance(manifest, PGM):
      intf_map = {}
      for node in manifest.nodes:
        dda("\"%s\" [label = \"%s\"]" % (node.sliver_id, node.name))
        for interface in node.interfaces:
          intf_map[interface.sliver_id] = (node, interface)

      for link in manifest.links:
        label = link.client_id
        name = link.client_id

        if link.vlan:
          label = "VLAN\n%s" % (link.vlan)
          name = link.vlan

        dda("\"%s\" [label=\"%s\",shape=doublecircle,fontsize=11.0]" % (name, label))

        for ref in link.interface_refs:
          dda("\"%s\" -> \"%s\" [taillabel=\"%s\"]" % (
            intf_map[ref][0].sliver_id, name,
            intf_map[ref][1].component_id.split(":")[-1]))
          dda("\"%s\" -> \"%s\"" % (name, intf_map[ref][0].sliver_id))


    elif isinstance(manifest, VTSM.Manifest):
      # TODO: We need to actually go through datapaths and such, but we can approximate for now
      for port in manifest.ports:
        if isinstance(port, VTSM.GREPort):
          pass
        elif isinstance(port, VTSM.PGLocalPort):
          dda("\"%s\" -> \"%s\" [taillabel=\"%s\"]" % (port.dpname, port.shared_vlan,
                                                       port.name))
          dda("\"%s\" -> \"%s\"" % (port.shared_vlan, port.dpname))
        elif isinstance(port, VTSM.InternalPort):
          dp = manifest.findTarget(port.dpname)
          if dp.mirror == port.client_id:
            continue # The other side will handle it, oddly
          # TODO: Handle mirroring into another datapath
          dda("\"%s\" -> \"%s\" [taillabel=\"%s\"]" % (port.dpname, port.remote_dpname,
                                                       port.name))
        elif isinstance(port, VTSM.InternalContainerPort):
          # Check to see if the other side is a mirror into us
          dp = manifest.findTarget(port.remote_dpname)
          if isinstance(dp, VTSM.ManifestDatapath):
            if port.remote_client_id == dp.mirror:
              remote_port_name = port.remote_client_id.split(":")[-1]
              dda("\"%s\" -> \"%s\" [headlabel=\"%s\",taillabel=\"%s\",style=dashed]" % (
                            port.remote_dpname, port.dpname, port.name, remote_port_name))
              continue

          # No mirror, draw as normal
          dda("\"%s\" -> \"%s\" [taillabel=\"%s\"]" % (port.dpname, port.remote_dpname,
                                                       port.name))
        elif isinstance(port, VTSM.GenericPort):
          pass
        else:
          continue ### TODO: Unsupported Port Type

      for dp in manifest.datapaths:
        dda("\"%s\" [shape=rectangle]" % (dp.client_id))


  dda("}")

  return "\n".join(dot_data)

def loadContext (path = None, key_passphrase = None):
  import geni._coreutil as GCU
  from geni.aggregate import FrameworkRegistry
  from geni.aggregate.context import Context
  from geni.aggregate.user import User

  if path is None:
    path = GCU.getDefaultContextPath()
  else:
    path = os.path.expanduser(path)

  obj = json.load(open(path, "r"))

  version = _getdefault(obj, "version", 1)

  if key_passphrase is True:
    import getpass
    key_passphrase = getpass.getpass("Private key passphrase: ")

  if version == 1:
    cf = FrameworkRegistry.get(obj["framework"])()
    cf.cert = obj["cert-path"]
    if key_passphrase:
      cf.setKey(obj["key-path"], key_passphrase)
    else:
      cf.key = obj["key-path"]

    user = User()
    user.name = obj["user-name"]
    user.urn = obj["user-urn"]
    user.addKey(obj["user-pubkeypath"])

    context = Context()
    context.addUser(user)
    context.cf = cf
    context.project = obj["project"]

  elif version == 2:
    context = Context()

    fobj = obj["framework-info"]
    cf = FrameworkRegistry.get(fobj["type"])()
    cf.cert = fobj["cert-path"]
    if key_passphrase:
      cf.setKey(fobj["key-path"], key_passphrase)
    else:
      cf.key = fobj["key-path"]
    context.cf = cf
    context.project = fobj["project"]

    ulist = obj["users"]
    for uobj in ulist:
      user = User()
      user.name = uobj["username"]
      user.urn = _getdefault(uobj, "urn", None)
      klist = uobj["keys"]
      for keypath in klist:
        user.addKey(keypath)
      context.addUser(user)

  from cryptography import x509
  from cryptography.hazmat.backends import default_backend
  cert = x509.load_pem_x509_certificate(open(context._cf.cert, "rb").read(), default_backend())
  if cert.not_valid_after < datetime.datetime.now():
    print("***WARNING*** Client SSL certificate supplied in this context is expired")
  return context


def hasDataContext ():
  import geni._coreutil as GCU

  path = GCU.getDefaultContextPath()
  return os.path.exists(path)


class MissingPublicKeyError(Exception):
  def __str__ (self):
    return "Your bundle does not appear to contain an SSH public key.  You must supply a path to one."


class PathNotFoundError(Exception):
  def __init__ (self, path):
    self._path = path

  def __str__ (self):
    return "The path %s does not exist." % (self._path)


def buildContextFromBundle (bundle_path, pubkey_path = None, cert_pkey_path = None):
  import geni._coreutil as GCU

  HOME = os.path.expanduser("~")

  # Create the .bssw directories if they don't exist
  DEF_DIR = GCU.getDefaultDir()

  zf = zipfile.ZipFile(os.path.expanduser(bundle_path))

  zip_pubkey_path = None
  if pubkey_path is None:
    # search for pubkey-like file in zip
    for fname in zf.namelist():
      if fname.startswith("ssh/public/") and fname.endswith(".pub"):
        zip_pubkey_path = fname
        break

    if not zip_pubkey_path:
      raise MissingPublicKeyError()

  # Get URN/Project/username from omni_config
  urn = None
  project = None

  oc = zf.open("omni_config")
  for l in oc.readlines():
    if l.startswith("urn"):
      urn = l.split("=")[1].strip()
    elif l.startswith("default_project"):
      project = l.split("=")[1].strip()
  
  uname = urn.rsplit("+")[-1]

  # Create .ssh if it doesn't exist
  try:
    os.makedirs("%s/.ssh" % (HOME), 0775)
  except OSError, e:
    pass

  # If a pubkey wasn't supplied on the command line, we may need to install both keys from the bundle
  pkpath = pubkey_path
  if not pkpath:
    if "ssh/private/id_geni_ssh_rsa" in zf.namelist():
      if not os.path.exists("%s/.ssh/id_geni_ssh_rsa" % (HOME)):
        # If your umask isn't already 0, we can't safely create this file with the right permissions
        with os.fdopen(os.open("%s/.ssh/id_geni_ssh_rsa" % (HOME), os.O_WRONLY | os.O_CREAT, 0o600), "w") as tf:
          tf.write(zf.open("ssh/private/id_geni_ssh_rsa").read())
    
    pkpath = "%s/.ssh/%s" % (HOME, zip_pubkey_path[len('ssh/public/'):])
    if not os.path.exists(pkpath):
        with open(pkpath, "w+") as tf:
          tf.write(zf.open(zip_pubkey_path).read())
  else:
    pkpath = os.path.expanduser(pubkey_path)
    if not os.path.exists(pkpath):
      raise PathNotFoundError(pkpath)

  # We write the pem into 'private' space
  zf.extract("geni_cert.pem", DEF_DIR)

  if cert_pkey_path is None:
    ckpath = "%s/geni_cert.pem" % (DEF_DIR)
  else:
    # Use user-provided key path instead of key inside .pem
    ckpath = os.path.expanduser(cert_pkey_path)
    if not os.path.exists(ckpath):
      raise PathNotFoundError(ckpath)

  cdata = {}
  cdata["framework"] = "portal"
  cdata["cert-path"] = "%s/geni_cert.pem" % (DEF_DIR)
  cdata["key-path"] = ckpath
  cdata["user-name"] = uname
  cdata["user-urn"] = urn
  cdata["user-pubkeypath"] = pkpath
  cdata["project"] = project
  json.dump(cdata, open("%s/context.json" % (DEF_DIR), "w+"))
