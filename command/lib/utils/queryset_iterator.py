import csv
import gc
from django.core.exceptions import ObjectDoesNotExist


def batch_qs(qs, batch_size=1000):
    """
    Returns a (start, end, total, queryset) tuple for each batch in the given
    queryset.

    Usage:
        # Make sure to order your querset
        article_qs = Article.objects.order_by('id')
        for start, end, total, qs in batch_qs(article_qs):
            print "Now processing %s - %s of %s" % (start + 1, end, total)
            for article in qs:
                print article.body
    """
    total = qs.count()
    for start in range(0, total, batch_size):
        end = min(start + batch_size, total)
        yield (start, end, total, qs[start:end])


def queryset_to_csv(outfile, queryset, fields):
    with open(outfile, 'w') as csvfile:
        writer = csv.writer(csvfile, delimiter=',')
        for start, end, total, qs in batch_qs(queryset, batch_size=2000):
            for obj in qs.all():
                row = []
                for field, value in fields.items():
                    if value:
                        row.append(value)
                    else:
                        row.append(getattr(obj, field))
                writer.writerow(row)



def queryset_iterator(queryset, chunk_size=1000):
    """
    Iterate over a Django Queryset ordered by the primary key
    This method loads a maximum of chunk_size (default: 1000) rows in it's
    memory at the same time while django normally would load all rows in it's
    memory. Using the iterator() method only causes it to not preload all the
    classes.
    Note that the implementation of the iterator does not support ordered query sets.
    """
    try:
        last_pk = queryset.order_by('-pk')[:1].get().pk
    except ObjectDoesNotExist:
        return

    pk = 0
    queryset = queryset.order_by('pk')
    while pk < last_pk:
        for row in queryset.filter(pk__gt=pk)[:chunk_size]:
            pk = row.pk
            yield row
        gc.collect()


def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i + n]
