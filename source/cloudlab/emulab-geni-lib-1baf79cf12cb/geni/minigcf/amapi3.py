# Copyright (c) 2015-2017  Barnstormer Softworks, Ltd.

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

# Streamlined implementation of xmlrpc calls to AM API v3-compliant aggregates
# Only uses python requests module, without a ton of extra SSL dependencies

from __future__ import absolute_import

import xmlrpclib

from .util import _rpcpost

# pylint: disable=unsubscriptable-object
def getversion (url, root_bundle, cert, key, options = None):
  if not options: options = {}
  req_data = xmlrpclib.dumps(options, methodname="GetVersion")
  return _rpcpost(url, req_data, (cert, key), root_bundle)

def poa (url, root_bundle, cert, key, creds, urns, action, options = None):
  if not options: options = {}
  if not isinstance(urns, list): urns = [urns]

  cred_list = []
  for cred in creds:
    cred_list.append({"geni_value" : open(cred.path, "rb").read(), "geni_type" : cred.type, "geni_version" : cred.version})

  req_data = xmlrpclib.dumps((urns, cred_list, action, options),
                             methodname="PerformOperationalAction")
  return _rpcpost(url, req_data, (cert, key), root_bundle)

def paa (url, root_bundle, cert, key, action, options = None):
  if not options: options = {}

  req_data = xmlrpclib.dumps((action, options),
                             methodname="PerformAggregateAction")
  return _rpcpost(url, req_data, (cert, key), root_bundle)

