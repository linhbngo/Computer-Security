# Copyright (c) 2014-2016  Barnstormer Softworks, Ltd.

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from __future__ import absolute_import

import os
import os.path

class _Registry(object):
  def __init__ (self):
    self._data = {}

  def register (self, name, obj):
    self._data[name] = obj

  def get (self, name):
    return self._data[name]


class AM(object):
  """Base class wrapping GENI AM APIv2 and AM APIv3 functionality."""

  class UnspecifiedComponentManagerError(Exception):
    def __str__ (self):
      return "AM object does not have a component manager ID specified"

  class InvalidRSpecPathError(Exception):
    def __init__ (self, path):
      super(AM.InvalidRSpecPathError, self).__init__()
      if len(path) > 400:
        path = path[:400] + "..."
      self.path = path
    def __str__ (self):
      return "RSpec object provided as path string, but path not found: %s" % (self.path)


  def __init__ (self, name, url, api, amtype, cmid=None):
    self.url = url
    self.name = name
    self._cmid = cmid
    self._apistr = api
    self._api = None
    self._typestr = amtype
    self._type = None

  @property
  def component_manager_id (self):
    if self._cmid:
      return self._cmid
    raise AM.UnspecifiedComponentManagerError()

  @property
  def api (self):
    if not self._api:
      self._api = APIRegistry.get(self._apistr)
    return self._api

  @property
  def amtype (self):
    if not self._type:
      self._type = AMTypeRegistry.get(self._typestr)
    return self._type

  def listresources (self, context, sname = None, available = False):
    """GENI AM APIv2 method to get available resources from an aggregate, or resources allocated to
    a specific sliver.

    Args:
      context: geni-lib context
      sname (str): Slice name (optional)
      available (bool): Only list available resources

    Returns:
      geni.rspec.RSpec:
        If `sname` is provided, `listresources` will return a manifest rspec for the given slice name.  Otherwise,
        `listresources` will return the advertisement rspec for the given aggregate.
    """

    rspec_data = self.api.listresources(context, self.url, sname, {"geni_available" : available})
    if sname is None:
      return self.amtype.parseAdvertisement(rspec_data)
    else:
      return self.amtype.parseManifest(rspec_data)

  def sliverstatus (self, context, sname):
    """GENI AM APIv2 method to get the status of a current sliver at the given aggregate.

    Args:
      context: geni-lib context
      sname (str): Slice name

    Returns:
      dict:
        Mapping of key/value pairs for status information the aggregate supports.
    """

    status = self.api.sliverstatus(context, self.url, sname)
    return status

  def renewsliver (self, context, sname, date):
    """GENI AM APIv2 method to renew a sliver until the given datetime.

    Args:
      context: geni-lib context
      sname (str): Slice name
      date (str): RFC 3339-compliant date string for new expiration date

    .. note::
      Aggregates may have maximum expiration limits, restricting how far in
      the future you can set your expiration.  This call may result in an
      error in such cases, or success with a sooner future date.
    """

    res = self.api.renewsliver(context, self.url, sname, date)
    return res

  def deletesliver (self, context, sname):
    """GENI AM APIv2 method to delete a resource reservation at this aggregate.

    Args:
      context: geni-lib context
      sname (str): Slice name
    """
    self.api.deletesliver(context, self.url, sname)

  def createsliver (self, context, sname, rspec):
    """GENI AM APIv2 method to reserve resources at this aggregate.

    Args:
      context: geni-lib context
      sname (str): Slice name
      rspec (geni.rspec.RSpec): Valid request RSpec
    """
    if isinstance(rspec, (str, unicode)):
      rspec = os.path.normpath(os.path.expanduser(rspec))
      if not os.path.exists(rspec):
        raise AM.InvalidRSpecPathError(rspec)
      rspec_data = open(rspec, "rb").read()
    else:
      rspec_data = rspec.toXMLString()
    res = self.api.createsliver(context, self.url, sname, rspec_data)
    return self.amtype.parseManifest(res)

  def getversion (self, context):
    """GENI AM API method to get the version information for this aggregate.

    Args:
      context: geni-lib context

    Returns:
      dict: Dictionary of key/value pairs with version information from this aggregate.
    """

    return self.api.getversion(context, self.url)


APIRegistry = _Registry()
AMTypeRegistry = _Registry()
FrameworkRegistry = _Registry()
