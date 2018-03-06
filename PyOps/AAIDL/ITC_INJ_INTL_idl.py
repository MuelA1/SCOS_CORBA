# Python stubs generated by omniidl from ITC_INJ_INTL.idl
# DO NOT EDIT THIS FILE!

import omniORB, _omnipy
from omniORB import CORBA, PortableServer
_0_CORBA = CORBA


_omnipy.checkVersion(4,2, __file__, 1)

try:
    property
except NameError:
    def property(*args):
        return None


# #include "IBASE.idl"
import IBASE_idl
_0_IBASE = omniORB.openModule("IBASE")
_0_IBASE__POA = omniORB.openModule("IBASE__POA")

# #include "ITC.idl"
import ITC_idl
_0_ITC = omniORB.openModule("ITC")
_0_ITC__POA = omniORB.openModule("ITC__POA")

# #include "ITC_INJ.idl"
import ITC_INJ_idl
_0_ITC_INJ = omniORB.openModule("ITC_INJ")
_0_ITC_INJ__POA = omniORB.openModule("ITC_INJ__POA")

#
# Start of module "ITC_INJ_INTL"
#
__name__ = "ITC_INJ_INTL"
_0_ITC_INJ_INTL = omniORB.openModule("ITC_INJ_INTL", r"ITC_INJ_INTL.idl")
_0_ITC_INJ_INTL__POA = omniORB.openModule("ITC_INJ_INTL__POA", r"ITC_INJ_INTL.idl")


# interface CommandInjectMngr
_0_ITC_INJ_INTL._d_CommandInjectMngr = (omniORB.tcInternal.tv_objref, "IDL:ITC_INJ_INTL/CommandInjectMngr:1.0", "CommandInjectMngr")
omniORB.typeMapping["IDL:ITC_INJ_INTL/CommandInjectMngr:1.0"] = _0_ITC_INJ_INTL._d_CommandInjectMngr
_0_ITC_INJ_INTL.CommandInjectMngr = omniORB.newEmptyClass()
class CommandInjectMngr (_0_ITC_INJ.CommandInjectMngr):
    _NP_RepositoryId = _0_ITC_INJ_INTL._d_CommandInjectMngr[1]

    def __init__(self, *args, **kw):
        raise RuntimeError("Cannot construct objects of this type.")

    _nil = CORBA.Object._nil


_0_ITC_INJ_INTL.CommandInjectMngr = CommandInjectMngr
_0_ITC_INJ_INTL._tc_CommandInjectMngr = omniORB.tcInternal.createTypeCode(_0_ITC_INJ_INTL._d_CommandInjectMngr)
omniORB.registerType(CommandInjectMngr._NP_RepositoryId, _0_ITC_INJ_INTL._d_CommandInjectMngr, _0_ITC_INJ_INTL._tc_CommandInjectMngr)

# CommandInjectMngr operations and attributes
CommandInjectMngr._d_setCallbackInf = ((omniORB.typeMapping["IDL:ITC_INJ/CommandInjectMngrView:1.0"], (omniORB.tcInternal.tv_string,0)), (), None)

# CommandInjectMngr object reference
class _objref_CommandInjectMngr (_0_ITC_INJ._objref_CommandInjectMngr):
    _NP_RepositoryId = CommandInjectMngr._NP_RepositoryId

    def __init__(self, obj):
        _0_ITC_INJ._objref_CommandInjectMngr.__init__(self, obj)

    def setCallbackInf(self, *args):
        return self._obj.invoke("setCallbackInf", _0_ITC_INJ_INTL.CommandInjectMngr._d_setCallbackInf, args)

omniORB.registerObjref(CommandInjectMngr._NP_RepositoryId, _objref_CommandInjectMngr)
_0_ITC_INJ_INTL._objref_CommandInjectMngr = _objref_CommandInjectMngr
del CommandInjectMngr, _objref_CommandInjectMngr

# CommandInjectMngr skeleton
__name__ = "ITC_INJ_INTL__POA"
class CommandInjectMngr (_0_ITC_INJ__POA.CommandInjectMngr):
    _NP_RepositoryId = _0_ITC_INJ_INTL.CommandInjectMngr._NP_RepositoryId


    _omni_op_d = {"setCallbackInf": _0_ITC_INJ_INTL.CommandInjectMngr._d_setCallbackInf}
    _omni_op_d.update(_0_ITC_INJ__POA.CommandInjectMngr._omni_op_d)

CommandInjectMngr._omni_skeleton = CommandInjectMngr
_0_ITC_INJ_INTL__POA.CommandInjectMngr = CommandInjectMngr
omniORB.registerSkeleton(CommandInjectMngr._NP_RepositoryId, CommandInjectMngr)
del CommandInjectMngr
__name__ = "ITC_INJ_INTL"

# interface TCinjectServerMngr
_0_ITC_INJ_INTL._d_TCinjectServerMngr = (omniORB.tcInternal.tv_objref, "IDL:ITC_INJ_INTL/TCinjectServerMngr:1.0", "TCinjectServerMngr")
omniORB.typeMapping["IDL:ITC_INJ_INTL/TCinjectServerMngr:1.0"] = _0_ITC_INJ_INTL._d_TCinjectServerMngr
_0_ITC_INJ_INTL.TCinjectServerMngr = omniORB.newEmptyClass()
class TCinjectServerMngr (_0_ITC_INJ.TCinjectServerMngr):
    _NP_RepositoryId = _0_ITC_INJ_INTL._d_TCinjectServerMngr[1]

    def __init__(self, *args, **kw):
        raise RuntimeError("Cannot construct objects of this type.")

    _nil = CORBA.Object._nil


_0_ITC_INJ_INTL.TCinjectServerMngr = TCinjectServerMngr
_0_ITC_INJ_INTL._tc_TCinjectServerMngr = omniORB.tcInternal.createTypeCode(_0_ITC_INJ_INTL._d_TCinjectServerMngr)
omniORB.registerType(TCinjectServerMngr._NP_RepositoryId, _0_ITC_INJ_INTL._d_TCinjectServerMngr, _0_ITC_INJ_INTL._tc_TCinjectServerMngr)

# TCinjectServerMngr operations and attributes
TCinjectServerMngr._d_addToPool = ((omniORB.typeMapping["IDL:ITC_INJ_INTL/CommandInjectMngr:1.0"], omniORB.tcInternal.tv_boolean), (omniORB.tcInternal.tv_long, ), None)
TCinjectServerMngr._d_makeAvailable = ((omniORB.tcInternal.tv_long, ), (), None)
TCinjectServerMngr._d_removeFromPool = ((omniORB.tcInternal.tv_long, ), (), None)

# TCinjectServerMngr object reference
class _objref_TCinjectServerMngr (_0_ITC_INJ._objref_TCinjectServerMngr):
    _NP_RepositoryId = TCinjectServerMngr._NP_RepositoryId

    def __init__(self, obj):
        _0_ITC_INJ._objref_TCinjectServerMngr.__init__(self, obj)

    def addToPool(self, *args):
        return self._obj.invoke("addToPool", _0_ITC_INJ_INTL.TCinjectServerMngr._d_addToPool, args)

    def makeAvailable(self, *args):
        return self._obj.invoke("makeAvailable", _0_ITC_INJ_INTL.TCinjectServerMngr._d_makeAvailable, args)

    def removeFromPool(self, *args):
        return self._obj.invoke("removeFromPool", _0_ITC_INJ_INTL.TCinjectServerMngr._d_removeFromPool, args)

omniORB.registerObjref(TCinjectServerMngr._NP_RepositoryId, _objref_TCinjectServerMngr)
_0_ITC_INJ_INTL._objref_TCinjectServerMngr = _objref_TCinjectServerMngr
del TCinjectServerMngr, _objref_TCinjectServerMngr

# TCinjectServerMngr skeleton
__name__ = "ITC_INJ_INTL__POA"
class TCinjectServerMngr (_0_ITC_INJ__POA.TCinjectServerMngr):
    _NP_RepositoryId = _0_ITC_INJ_INTL.TCinjectServerMngr._NP_RepositoryId


    _omni_op_d = {"addToPool": _0_ITC_INJ_INTL.TCinjectServerMngr._d_addToPool, "makeAvailable": _0_ITC_INJ_INTL.TCinjectServerMngr._d_makeAvailable, "removeFromPool": _0_ITC_INJ_INTL.TCinjectServerMngr._d_removeFromPool}
    _omni_op_d.update(_0_ITC_INJ__POA.TCinjectServerMngr._omni_op_d)

TCinjectServerMngr._omni_skeleton = TCinjectServerMngr
_0_ITC_INJ_INTL__POA.TCinjectServerMngr = TCinjectServerMngr
omniORB.registerSkeleton(TCinjectServerMngr._NP_RepositoryId, TCinjectServerMngr)
del TCinjectServerMngr
__name__ = "ITC_INJ_INTL"

#
# End of module "ITC_INJ_INTL"
#
__name__ = "ITC_INJ_INTL_idl"

_exported_modules = ( "ITC_INJ_INTL", )

# The end.
