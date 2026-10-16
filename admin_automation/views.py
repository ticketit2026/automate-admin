
@login_required
def letter_list(request):
    letters = InternalLetter.objects.select_related(
        'created_by',
        'assigned_to',
        'assigned_by',
        'approved_by',
        'rejected_by',
    )

    if not has_access(request.user, 'view_all_letters'):
        letters = letters.filter(
            Q(created_by=request.user)
            | Q(assigned_to=request.user)
        )

    search = request.GET.get('search', '').strip()
    document_type = request.GET.get('document_type', '').strip()
    status = request.GET.get('status', '').strip()

    if search:
        letters = letters.filter(
            Q(letter_number__icontains=search)
            | Q(title__icontains=search)
            | Q(content__icontains=search)
            | Q(sent_to__icontains=search)
        )

    if document_type:
        letters = letters.filter(document_type=document_type)

    if status:
        letters = letters.filter(status=status)

    context = {
        'letters': letters,
        'search': search,
        'document_type': document_type,
        'status': status,
        'document_type_choices': InternalLetter._meta.get_field(
            'document_type'
        ).choices,
        'can_create_letter': has_access(
            request.user, 'create_letter'
        ),
    }

    return render(
        request,
        'admin_automation/letter_list.html',
        context,
    )
