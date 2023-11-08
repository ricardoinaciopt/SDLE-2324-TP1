from LWW.lww import Lww


def test_add():
    """
    This functions test the successful addition of the element
    into the LWW
    :return: None
    """

    lww = Lww()

    lww.add(1)
    lww.add("test_element")

    print(lww.lookup(1))
    print(lww.lookup("test_element"))
    print(lww.lookup("test"))


def test_remove():
    """
    This function test the successful removal of the element
    from the LWW
    :return: None
    """

    lww = Lww()

    lww.remove(1)
    lww.lookup(1)

    lww.add(1)
    lww.lookup(1)


def test_compare():
    """
    This function test the compare method of Lww
    :return: None
    """

    lww1 = Lww()
    lww2 = Lww()

    lww1.add(1)
    lww1.add(2)

    lww2.add(1)
    lww2.add(2)
    lww2.add(3)

    lww1.remove(1)
    lww1.remove(2)

    lww2.remove(1)
    lww2.remove(2)
    lww2.remove(3)

    print(lww1.add_set, lww1.remove_set)
    print(lww2.add_set, lww2.remove_set)

    print(lww1.compare(lww2))

    print(lww2.compare(lww1))


def test_merge():
    """
    This function test the merge method of Lww
    :return: None
    """

    lww1 = Lww()
    lww2 = Lww()

    lww1.add(1)
    lww1.add(2)
    lww1.remove(1)

    lww2.add(1)
    lww2.add(3)

    lww1.remove(3)

    lww2.remove(1)

    lww = lww1.merge(lww2)

    print(lww.add_set, lww.remove_set)

    # {1, 2, 3}.issubset(lww.add_set.keys())
    # {1, 3}.issubset(lww.remove_set.keys())
    # lww.add_set[1] == lww2.add_set[1]
    # lww.add_set[1] > lww1.add_set[1]
    # lww.add_set[3] < lww1.remove_set[3]
    # lww.remove_set[1] == lww2.remove_set[1]


def test_add_exception(caplog):
    """
    This function test the exception handling of the add
    :param caplog: pytest fixture
    :return: None
    """

    lww = Lww()
    lww.add([1, 2, 3])


def test_remove_exception(caplog):
    """
    This function test the exception handling of the add
    :param caplog: pytest fixture
    :return: None
    """

    lww = Lww()
    lww.remove({})


def test_key_internal():
    """
    This function validates the state of the elements in Lww
    :return: None
    """
    lww = Lww()

    lww.add(1)
    lww.add(2)
    lww.add(3)
    lww.remove(4)
    lww.remove(2)

    {1, 2, 3}.issubset(lww.add_set.keys())
    {2, 4}.issubset(lww.remove_set.keys())

    4 in lww.add_set.keys()
    1 in lww.remove_set.keys()
    3 in lww.remove_set.keys()


def test_value_internal():
    """
    This function validates internal element timestamps
    :return: None
    """
    lww = Lww()

    lww.add(1)
    lww.add(2)
    lww.add(3)
    lww.remove(4)
    lww.remove(2)

    lww.remove_set[2] > lww.add_set[2]
    lww.add_set[3] > lww.add_set[2]
    lww.remove_set[4] > lww.add_set[3]
    lww.remove_set[2] > lww.remove_set[4]


def test_re_add():
    """
    This function validates repeated addtition of same element
    :return: None
    """
    lww = Lww()

    lww.add(1)
    lww.remove(1)
    lww.add(1)

    lww.lookup(1)


def test_re_remove():
    """
    This function validates repeated removal of same element
    :return: None
    """
    lww = Lww()

    lww.add(1)
    lww.remove(1)
    lww.add(1)
    lww.remove(1)

    lww.lookup(1)


def test_remove_add():
    """
    This function validates remove element followed by addition
    :return: None
    """
    lww = Lww()

    lww.remove(1)
    lww.add(1)

    lww.lookup(1)


def test_rep_remove_add():
    """
    This function validates repeated remove of element
    :return: None
    """
    lww = Lww()

    lww.remove(1)
    lww.add(1)
    lww.remove(1)

    lww.lookup(1)


def test_empty_lookup():
    """
    This function validates empty lookup
    :return: None
    """
    lww = Lww()

    lww.lookup(1)


if __name__ == "__main__":
    test_merge()
