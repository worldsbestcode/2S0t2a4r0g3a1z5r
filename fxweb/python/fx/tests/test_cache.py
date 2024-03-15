from nose.tools import *
from cache import Cache 
from librk import ManagedObjectUtils, ManagedObject, ExcryptMessage

class TestCache(object):
    """
    Object Cache tests
    """
    @classmethod
    def setup_class(klass):
        pass

    @classmethod
    def teardown_class(klass):
        pass

    def setUp(self):
        pass

    def teardown(self):
        pass

    def test_update_cache_single_object(self):
        cache = Cache()
        mo = ManagedObjectUtils.createObjectFromType(ManagedObject.CARD, 0)
        em = ExcryptMessage()
        mo.toMessage(em)
        cache.update_cache([em.getText()], ManagedObject.CARD)

        assert_equals(cache.size(ManagedObject.CARD), 1)

    def test_get_object_of_card_type(self):
        cache = Cache()
        mo = ManagedObjectUtils.createObjectFromType(ManagedObject.CARD, 0)
        em = ExcryptMessage()
        mo.toMessage(em)
        cache.update_cache([em.getText()], ManagedObject.CARD)
        mos = cache.get_objects(ManagedObject.CARD)

        assert_equals(len(mos), 1)

