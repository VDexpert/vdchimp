from random import randint
from django.core.cache import cache
from django.conf import settings


def cache_home_posts(model):
    if settings.CACHE_ENABLED:
        key = f'home_post_list'
        cache_data = cache.get(key)

        if cache_data is None:
            count_post = model.objects.all().filter(status=model.STATUS_ACTIVE).count()

            rand_post_id = []
            while len(rand_post_id) < 6:
                x = randint(1, count_post)
                if x in rand_post_id:
                    continue
                rand_post_id.append(x)

            post_list = []
            for num in rand_post_id:
                post_list.append(model.objects.all().get(id=num))

            cache.set(key, post_list)

            return post_list

        return cache_data

def cache_blog(model):
    if settings.CACHE_ENABLED:
        key = f'post_list'
        cache_data = cache.get(key)

        if cache_data is None:
            queryset = model.objects.all().filter(status=model.STATUS_ACTIVE).order_by('-create_at', '-id')

            cache.set(key, queryset)

            return queryset

        return cache_data