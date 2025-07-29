from app import database

# Eliminados imports y funciones que borraban el directorio db_json

def test_save_and_load_json():
    data = {"foo": "bar", "num": 42}
    database.save_json("testfile", data)
    loaded = database.load_json("testfile")
    assert loaded == data

def test_load_nonexistent_json():
    assert database.load_json("no_such_file") is None

# Test de sobrescritura
def test_overwrite_json():
    data1 = {"a": 1}
    data2 = {"a": 2, "b": 3}
    database.save_json("overwrite", data1)
    database.save_json("overwrite", data2)
    loaded = database.load_json("overwrite")
    assert loaded == data2
