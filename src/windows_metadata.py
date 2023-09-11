import pythoncom
from pathlib import Path

from win32comext.propsys import propsys
from win32comext.shell import shellcon
from contextlib import contextmanager

@contextmanager
def property_context(filepath: str):
    filepath = str(Path(filepath).absolute())
    ps = propsys.SHGetPropertyStoreFromParsingName(filepath, None, shellcon.GPS_READWRITE, propsys.IID_IPropertyStore) # type:ignore
    try:
        yield ps
    finally:
        ps.Commit()

def gen_propvariant_value(item) -> propsys.PROPVARIANTType:
    if isinstance(item, (list, tuple)):
        prop_type = pythoncom.VT_VECTOR | pythoncom.VT_BSTR
    elif isinstance(item, str):
        prop_type = pythoncom.VT_BSTR
    else:
        raise ValueError("Unhandled type: %s", type(item))
    return propsys.PROPVARIANTType(item, prop_type) # type:ignore

def set_metadata(filepath: str, name: str, value: str | list[str]):
    with property_context(filepath) as ps:
        prop_key = propsys.PSGetPropertyKeyFromName(name)
        prop_value = gen_propvariant_value(value)
        ps.SetValue(prop_key, prop_value)
    
# set_metadata('./test.jpg', 'System.Comment', 'Hello world!')
# set_metadata('./test.jpg', 'System.Keywords', ['Hello', 'World!'])