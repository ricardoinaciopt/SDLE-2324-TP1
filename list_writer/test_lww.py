from LWW.lww import Lww
import time


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
    # different versions of same list
    lww1 = Lww()
    lww2 = Lww()

    lww1.add(1)
    lww1.add(2)

    lww1.remove(1)

    time.sleep(3)
    lww2.add(1)
    lww2.add(3)

    lww = lww1.merge(lww2)

    print(lww.get_full_list())


if __name__ == "__main__":
    test_merge()
