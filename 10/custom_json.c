#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <string.h>
#include <ctype.h>
#include <math.h>

typedef struct {
    const char *start;
    const char *end;
    const char *current;
} JsonParser;

static void skip_whitespace(JsonParser *parser) {
    while (parser->current < parser->end && isspace(*parser->current)) {
        parser->current++;
    }
}

static int parse_string(JsonParser *parser, PyObject **value) {
    if (*parser->current != '"') {
        return 0;
    }
    parser->current++;

    const char *start = parser->current;
    while (parser->current < parser->end && *parser->current != '"') {
        if (*parser->current == '\\') {
            parser->current++;
        }
        if (parser->current < parser->end) {
            parser->current++;
        }
    }

    if (parser->current >= parser->end) {
        return 0;
    }

    PyObject *str = PyUnicode_FromStringAndSize(start, parser->current - start);
    if (!str) {
        return 0;
    }

    *value = str;
    parser->current++;
    return 1;
}

static int parse_number(JsonParser *parser, PyObject **value) {
    const char *start = parser->current;
    char *endptr;
    double d = strtod(start, &endptr);

    if (endptr == start) {
        return 0;
    }

    parser->current = endptr;

    if (d == (long long)d) {
        *value = PyLong_FromLongLong((long long)d);
    } else {
        *value = PyFloat_FromDouble(d);
    }

    return *value != NULL;
}

static int parse_keyword(JsonParser *parser, PyObject **value, const char *keyword, PyObject *result) {
    size_t len = strlen(keyword);
    if (parser->current + len <= parser->end && strncmp(parser->current, keyword, len) == 0) {
        *value = result;
        Py_INCREF(result);
        parser->current += len;
        return 1;
    }
    return 0;
}

static int parse_value(JsonParser *parser, PyObject **value);

static int parse_array(JsonParser *parser, PyObject **value) {
    if (*parser->current != '[') {
        return 0;
    }
    parser->current++;

    PyObject *list = PyList_New(0);
    if (!list) {
        return 0;
    }

    skip_whitespace(parser);
    if (*parser->current == ']') {
        parser->current++;
        *value = list;
        return 1;
    }

    while (1) {
        PyObject *item = NULL;
        if (!parse_value(parser, &item)) {
            Py_DECREF(list);
            return 0;
        }

        if (PyList_Append(list, item) < 0) {
            Py_DECREF(item);
            Py_DECREF(list);
            return 0;
        }
        Py_DECREF(item);

        skip_whitespace(parser);
        if (*parser->current == ']') {
            parser->current++;
            *value = list;
            return 1;
        }

        if (*parser->current != ',') {
            Py_DECREF(list);
            return 0;
        }
        parser->current++;
        skip_whitespace(parser);
    }
}

static int parse_object(JsonParser *parser, PyObject **value) {
    if (*parser->current != '{') {
        return 0;
    }
    parser->current++;

    PyObject *dict = PyDict_New();
    if (!dict) {
        return 0;
    }

    skip_whitespace(parser);
    if (*parser->current == '}') {
        parser->current++;
        *value = dict;
        return 1;
    }

    while (1) {
        PyObject *key = NULL;
        if (!parse_string(parser, &key)) {
            Py_DECREF(dict);
            return 0;
        }

        skip_whitespace(parser);
        if (*parser->current != ':') {
            Py_DECREF(key);
            Py_DECREF(dict);
            return 0;
        }
        parser->current++;

        skip_whitespace(parser);
        PyObject *val = NULL;
        if (!parse_value(parser, &val)) {
            Py_DECREF(key);
            Py_DECREF(dict);
            return 0;
        }

        if (PyDict_SetItem(dict, key, val) < 0) {
            Py_DECREF(key);
            Py_DECREF(val);
            Py_DECREF(dict);
            return 0;
        }

        Py_DECREF(key);
        Py_DECREF(val);

        skip_whitespace(parser);
        if (*parser->current == '}') {
            parser->current++;
            *value = dict;
            return 1;
        }

        if (*parser->current != ',') {
            Py_DECREF(dict);
            return 0;
        }
        parser->current++;
        skip_whitespace(parser);
    }
}

static int parse_value(JsonParser *parser, PyObject **value) {
    skip_whitespace(parser);

    if (*parser->current == '{') {
        return parse_object(parser, value);
    } else if (*parser->current == '[') {
        return parse_array(parser, value);
    } else if (*parser->current == '"') {
        return parse_string(parser, value);
    } else if (*parser->current == '-' || isdigit(*parser->current)) {
        return parse_number(parser, value);
    } else if (parse_keyword(parser, value, "true", Py_True)) {
        return 1;
    } else if (parse_keyword(parser, value, "false", Py_False)) {
        return 1;
    } else if (parse_keyword(parser, value, "null", Py_None)) {
        return 1;
    }

    return 0;
}

static PyObject *custom_json_loads(PyObject *self, PyObject *args) {
    const char *json_str;
    Py_ssize_t length;

    if (!PyArg_ParseTuple(args, "s#", &json_str, &length)) {
        return NULL;
    }

    JsonParser parser = {
        .start = json_str,
        .end = json_str + length,
        .current = json_str
    };

    PyObject *result = NULL;
    if (!parse_value(&parser, &result)) {
        PyErr_SetString(PyExc_TypeError, "Expected object or value");
        return NULL;
    }

    skip_whitespace(&parser);
    if (parser.current != parser.end) {
        Py_DECREF(result);
        PyErr_SetString(PyExc_TypeError, "Unexpected trailing characters");
        return NULL;
    }

    return result;
}

static int serialize_value(PyObject *value, PyObject **str_obj);

static int serialize_list(PyObject *list, PyObject **str_obj) {
    PyObject *result = PyUnicode_FromString("[");
    if (!result) return 0;

    Py_ssize_t size = PyList_Size(list);
    for (Py_ssize_t i = 0; i < size; i++) {
        PyObject *item = PyList_GetItem(list, i);
        PyObject *item_str = NULL;

        if (!serialize_value(item, &item_str)) {
            Py_DECREF(result);
            return 0;
        }

        if (i > 0) {
            PyObject *temp = PyUnicode_Concat(result, PyUnicode_FromString(", "));
            Py_DECREF(result);
            result = temp;
            if (!result) {
                Py_DECREF(item_str);
                return 0;
            }
        }

        PyObject *temp = PyUnicode_Concat(result, item_str);
        Py_DECREF(result);
        Py_DECREF(item_str);
        result = temp;
        if (!result) {
            return 0;
        }
    }

    PyObject *temp = PyUnicode_Concat(result, PyUnicode_FromString("]"));
    Py_DECREF(result);
    *str_obj = temp;
    return temp != NULL;
}

static int serialize_dict(PyObject *dict, PyObject **str_obj) {
    PyObject *result = PyUnicode_FromString("{");
    if (!result) return 0;

    PyObject *key = NULL, *value = NULL;
    Py_ssize_t pos = 0;
    int first = 1;

    while (PyDict_Next(dict, &pos, &key, &value)) {
        if (!PyUnicode_Check(key)) {
            Py_DECREF(result);
            PyErr_SetString(PyExc_TypeError, "Dictionary key must be string");
            return 0;
        }

        PyObject *key_str = PyUnicode_AsUTF8String(key);
        if (!key_str) {
            Py_DECREF(result);
            return 0;
        }

        const char *key_cstr = PyBytes_AsString(key_str);
        PyObject *item_str = NULL;

        if (!serialize_value(value, &item_str)) {
            Py_DECREF(key_str);
            Py_DECREF(result);
            return 0;
        }

        PyObject *pair = PyUnicode_FromFormat("\"%s\": %U", key_cstr, item_str);
        Py_DECREF(key_str);
        Py_DECREF(item_str);
        if (!pair) {
            Py_DECREF(result);
            return 0;
        }

        if (!first) {
            PyObject *temp = PyUnicode_Concat(result, PyUnicode_FromString(", "));
            Py_DECREF(result);
            result = temp;
            if (!result) {
                Py_DECREF(pair);
                return 0;
            }
        }

        PyObject *temp = PyUnicode_Concat(result, pair);
        Py_DECREF(result);
        Py_DECREF(pair);
        result = temp;
        if (!result) {
            return 0;
        }

        first = 0;
    }

    PyObject *temp = PyUnicode_Concat(result, PyUnicode_FromString("}"));
    Py_DECREF(result);
    *str_obj = temp;
    return temp != NULL;
}

static int serialize_value(PyObject *value, PyObject **str_obj) {
    if (value == Py_None) {
        *str_obj = PyUnicode_FromString("null");
    } else if (value == Py_True) {
        *str_obj = PyUnicode_FromString("true");
    } else if (value == Py_False) {
        *str_obj = PyUnicode_FromString("false");
    } else if (PyUnicode_Check(value)) {
        PyObject *utf8 = PyUnicode_AsUTF8String(value);
        if (!utf8) return 0;
        const char *str = PyBytes_AsString(utf8);
        *str_obj = PyUnicode_FromFormat("\"%s\"", str);
        Py_DECREF(utf8);
    } else if (PyLong_Check(value)) {
        *str_obj = PyObject_Str(value);
    } else if (PyFloat_Check(value)) {
        *str_obj = PyObject_Str(value);
    } else if (PyList_Check(value) || PyTuple_Check(value)) {
        return serialize_list(value, str_obj);
    } else if (PyDict_Check(value)) {
        return serialize_dict(value, str_obj);
    } else {
        PyErr_SetString(PyExc_TypeError, "Unsupported type for JSON serialization");
        return 0;
    }

    return *str_obj != NULL;
}

static PyObject *custom_json_dumps(PyObject *self, PyObject *args) {
    PyObject *obj;
    if (!PyArg_ParseTuple(args, "O", &obj)) {
        return NULL;
    }

    PyObject *result = NULL;
    if (!serialize_value(obj, &result)) {
        return NULL;
    }

    return result;
}

static PyMethodDef CustomJsonMethods[] = {
    {"loads", custom_json_loads, METH_VARARGS, "Parse JSON string into Python object"},
    {"dumps", custom_json_dumps, METH_VARARGS, "Serialize Python object to JSON string"},
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef custom_json_module = {
    PyModuleDef_HEAD_INIT,
    "custom_json",
    NULL,
    -1,
    CustomJsonMethods
};

PyMODINIT_FUNC PyInit_custom_json(void) {
    return PyModule_Create(&custom_json_module);
}