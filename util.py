from models import Report


def en(s):
    if isinstance(s, unicode):
        return s.encode('utf-8', 'ignore')
    else:
        return str(s)


def get_reports_with_permissions(user, action):
    reports = []
    for r in Report.objects.all().order_by('name'):
        if user.has_perm('feedstrap.can_%s_report%s' % (action, str(r.pk))):
            reports.append(r)
        elif action == 'edit':
            r.hidden = True
            reports.append(r)
        elif action == 'see':
            if not r.restricted: reports.append(r)

    return reports

def generate_choices(model, displayed_value='name', real_value="pk"):
    options = ()
    for r in model.objects.all():
        options += ((str(getattr(r, real_value)), getattr(r, displayed_value)),)
    return tuple(sorted(set(options), key=lambda opt: opt[1]))

