# -*- coding: utf-8 -*-
'''
Created on Mar 11, 2012

@author: moloch

    Copyright 2012 Root the Box

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
'''


import xml.etree.cElementTree as ET

from uuid import uuid4
from netaddr import IPAddress
from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import synonym
from sqlalchemy.types import Integer, String
from models import dbsession
from models.BaseModels import DatabaseObject
from tornado import netutil


class IpAddress(DatabaseObject):
    ''' Wraps the netaddr IPAddress class '''

    uuid = Column(String(36), unique=True, nullable=False, default=lambda: str(uuid4()))
    box_id = Column(Integer, ForeignKey('box.id'), nullable=False)
    _address = Column(String(40), unique=True)
    _ip_address = None

    @classmethod
    def all(cls):
        ''' Returns a list of all objects in the database '''
        return dbsession.query(cls).all()

    @classmethod
    def by_id(cls, _id):
        ''' Returns a the object with id of _id '''
        return dbsession.query(cls).filter_by(id=_id).first()

    @classmethod
    def by_uuid(cls, _uuid):
        ''' Return and object based on a _uuid '''
        return dbsession.query(cls).filter_by(uuid=_uuid).first()

    @classmethod
    def by_address(cls, address):
        ''' Return and object based on an address '''
        return dbsession.query(cls).filter_by(_address=address).first()

    @property
    def address(self):
        if self._ip_address is None:
            self._ip_address = IPAddress(self._address)
        return self._ip_address.format()

    @address.setter
    def address(self, value):
        ip = IPAddress(value)
        if ip.is_loopback():
            raise ValueError("You cannot use a loopback address")
        if ip.is_multicast():
            raise ValueError("You cannot use a multicast address")
        self._address = value

    @property
    def version(self):
        if self._ip_address is None:
            self._ip_address = IPAddress(self._address)
        return self._ip_address.version

    @property
    def is_private(self):
        if self._ip_address is None:
            self._ip_address = IPAddress(self._address)
        return self._ip_address.is_private()

    def to_xml(self, parent):
        ip_elem = ET.SubElement(parent, "ip")
        ip_elem.set("version", str(self.version))
        ET.SubElement(ip_elem, "address").text = self.address

    def __repr__(self):
        return "<IpAddress - %s>" % self.address

    def __str__(self):
        return self._address

    def __eq__(self, other):
        return self._address == other._address

    def __ne__(self, other):
        return not self == other
