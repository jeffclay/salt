"""
Tests for win_certutil
"""

import pytest
import salt.exceptions

pytestmark = [
    pytest.mark.windows_whitelisted,
    pytest.mark.skip_unless_on_windows,
]


@pytest.fixture(scope="module")
def certutil(modules):
    return modules.certutil


@pytest.fixture(scope="module")
def cert_file():
    # This is the binary contents of a self-signed cert for testing
    binary_data = b'0\x82\x03\x0e0\x82\x01\xf6\xa0\x03\x02\x01\x02\x02\x10'\
                  b'[\xe1\xcc]Q\xb7\x8d\xbdI\xa0\xb7\xc0\rD\x80m0\r\x06\t*'\
                  b'\x86H\x86\xf7\r\x01\x01\x0b\x05\x000\x1a1\x180\x16\x06'\
                  b'\x03U\x04\x03\x0c\x0fTestCertificate0\x1e\x17'\
                  b'\r220120174254Z\x17\r230120180254Z0\x1a1\x180\x16\x06\x03U'\
                  b'\x04\x03\x0c\x0fTestCertificate0\x82\x01"0\r\x06\t*\x86H'\
                  b'\x86\xf7\r\x01\x01\x01\x05\x00\x03\x82\x01\x0f\x000\x82'\
                  b'\x01\n\x02\x82\x01\x01\x00\xb8x@YBP\x9f\x9c\x0e\n\xad'\
                  b'\xd0l6\xc4\x9c\x7f#\x97\xbck@b\\\xa1\x94\xecR\x85Xq\xe4H'\
                  b'\x0c\xfa\x1b]\xb8\x14\x14x\x05\xb7\xe6\xb6t\x07j\xda0\xd0'\
                  b'\xb5\xc8\xdf\xe8\xad\xeb4qa\x86\xefw\x19\xf0\x9a%\xb8!\x81'\
                  b'\xc2\xcbd\x81,\xbd\xe1a\x91\x822\nh\x88\x9d\xb7\x82 \xe8'\
                  b'\x0f\x91\x13\xc8\xc0xir\xf8\x90Yc\x8f3\xe9\xdc\xa3\xbc+'\
                  b'\xea/\x02\n\x94\xde\xba\xbb\xcb0\x98Z\xbc\xeeK\xab\xc5'\
                  b'\xba,\x0f\x7f}6\xb9$|\xdd=\xdaN\xff]N\xe3\xbd\x00\xee?H'\
                  b'\xdav\xa9\x95\xb8Vd\xf9=\x01\x16K\xb8\xa0C%\x1e[\x18\'\xb4'\
                  b'\x17Vi\xee\x97[\xf9\xa8MM\xfb\x88\x9fc\xbb\x08\xa7!\xc0U'\
                  b'\xa8\xfc\nx:\xbc\x8f\x14\x0eF\x1f\x85Ba\x8b\xa3\xd7\xc4<'\
                  b'\xcaN\xd1;y\xd0\x1a\xeb\xd2\x91c\x94\xee%\xc8\x82\x85\x92'\
                  b'\x88\xec\x1d\nh\xa9q|E\x1a\xaf\x16\x89!i\x19\'\xb7t{\x11'\
                  b'\xe8\xb8\xee\xa9\x97\xf4\x1c\xfa\x92-\x02\x03\x01\x00\x01'\
                  b'\xa3P0N0\x0e\x06\x03U\x1d\x0f\x01\x01\xff\x04\x04\x03\x02'\
                  b'\x05\xa00\x1d\x06\x03U\x1d%\x04\x160\x14\x06\x08+\x06\x01'\
                  b'\x05\x05\x07\x03\x02\x06\x08+\x06\x01\x05\x05\x07\x03\x010'\
                  b'\x1d\x06\x03U\x1d\x0e\x04\x16\x04\x14\xefy\x97r\x16\xadg\r'\
                  b'\x85\xea\xfe\xa8y[29\x0b%\xdfB0\r\x06\t*\x86H\x86\xf7\r'\
                  b'\x01\x01\x0b\x05\x00\x03\x82\x01\x01\x00\x93)\x0c$\xeb\xf7'\
                  b'\x02\x9fSf^[\t2\xd3\xdf\xcc~b\xdd\xd3\x1e<\x91\xbc\x93'\
                  b'\x87Z\x8ciC/\x87\x85\xf4\x18\xe0j\xae\xf3\x1c\xa7\xab\xf7'\
                  b'\xfd\xd9\xeb\x11:}Ys\x8f\xc9\\\xea\x17\xbb\x957\x9b\xef'\
                  b'\x17E]RwY\x10\x8b\x08\xc5\xa6\xc9\x05[\xe7\x11\xf3"2\xd3'\
                  b'\xca\xf6\x05\x8a2\xc1S\x1e\xf0\xdb\xfa,\xfc\x80\xb88-!\x07'\
                  b'\xe5\x81mc\'\xca\x16@\x16\xf7\x9b\xc5\x95V;$\x95\xeab\xea'\
                  b'\x1eX\x1dU\x97\x87\xc0\x17\xd0n\x01c@\x88z\xec\x9ep\x19'\
                  b'\x02I\xf6\xe4\xddr\xc3(\xb9\x98\x97$\xb8\xf3g\x16\x05\xa7'\
                  b'\x04\xf7\x15\x9a\xed!\x02\xd76\xb2nC\x04}sV=,\xd5\x8e'\
                  b'\xb8hG\x99\xcb-x\x0e\x05h\xee;\xcdp\x13\xfc)\xdb\xa9o\xb0'\
                  b'\x1c\x0e\x86\xb2\r\xc5.\xb1\x036\t\xd3l&\xd1\x13\xc1\xc1'\
                  b'\x12\xfb\xc0\xab<\xaf\x04\x0eIW\xb8<OD\xfe"(U\xc2&\xa8\xd8'\
                  b'\x9bkY\xdb~\xf8\xad\xb7\xa8Mu\xb6\xef\x89\xf2\xbeM'
    with pytest.helpers.temp_file("TestCertificate.cer") as cert_file:
        with open(str(cert_file), "wb") as fh:
            fh.write(binary_data)
        yield cert_file


@pytest.fixture(scope="function")
def clean_store(certutil, cert_file):
    certutil.del_store(source=str(cert_file), store="TrustedPublisher")
    serials = certutil.get_stored_cert_serials(store="TrustedPublisher")
    assert "5be1cc5d51b78dbd49a0b7c00d44806d" not in serials
    yield
    certutil.del_store(source=str(cert_file), store="TrustedPublisher")


@pytest.fixture(scope="function")
def populate_store(certutil, cert_file):
    certutil.add_store(source=str(cert_file), store="TrustedPublisher")
    serials = certutil.get_stored_cert_serials(store="TrustedPublisher")
    assert "5be1cc5d51b78dbd49a0b7c00d44806d" in serials
    yield
    certutil.del_store(source=str(cert_file), store="TrustedPublisher")


@pytest.mark.destructive_test
def test_get_stored_cert_serials(certutil, populate_store):
    serials = certutil.get_stored_cert_serials("TrustedPublisher")
    assert "5be1cc5d51b78dbd49a0b7c00d44806d" in serials


def test_get_stored_cert_serials_not_present(certutil, clean_store):
    serials = certutil.get_stored_cert_serials("TrustedPublisher")
    assert "5be1cc5d51b78dbd49a0b7c00d44806d" not in serials


def test_get_cert_serial(certutil, cert_file):
    serial = certutil.get_cert_serial(str(cert_file))
    assert serial == "5be1cc5d51b78dbd49a0b7c00d44806d"


def test_get_cert_serial_not_found(certutil, cert_file):
    with pytest.raises(salt.exceptions.CommandExecutionError) as exc:
        certutil.get_cert_serial(str(cert_file.parent / "absent.cer"))
    assert "cert_file not found" in exc.value.message


@pytest.mark.destructive_test
def test_add_store(certutil, cert_file, clean_store):
    certutil.add_store(source=str(cert_file), store="TrustedPublisher")
    serials = certutil.get_stored_cert_serials(store="TrustedPublisher")
    assert "5be1cc5d51b78dbd49a0b7c00d44806d" in serials


@pytest.mark.destructive_test
def test_del_store(certutil, cert_file, populate_store):
    certutil.del_store(source=str(cert_file), store="TrustedPublisher")
    serials = certutil.get_stored_cert_serials(store="TrustedPublisher")
    assert "5be1cc5d51b78dbd49a0b7c00d44806d" not in serials
