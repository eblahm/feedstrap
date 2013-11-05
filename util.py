from models import Report


def en(s):
    if isinstance(s, unicode):
        return s.encode('utf-8', 'ignore')
    else:
        return str(s)


def get_reports_with_permissions(user, action):
    reports = []
    for r in Report.objects.all():
        if user.has_perm('feedstrap.can_%s_%s_report' % (action, r.name)):
            reports.append(r)
        elif action == 'edit':
            r.hidden = True
            reports.append(r)
        elif action == 'see':
            if not r.restricted: reports.append(r)

    return reports

