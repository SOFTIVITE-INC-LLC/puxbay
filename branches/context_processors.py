from accounts.models import Branch

def branch_currency(request):
    """
    Context processor to make branch currency available globally in templates.
    Extracts currency information from the branch context if available.
    """
    context = {}
    
    # Try to get branch from request context (set by views)
    branch = getattr(request, 'branch', None)
    
    # If no branch in request, try to extract from URL parameters
    if not branch and hasattr(request, 'resolver_match'):
        if request.resolver_match and 'branch_id' in request.resolver_match.kwargs:
            branch_id = request.resolver_match.kwargs.get('branch_id')
            try:
                branch = Branch.objects.get(id=branch_id)
            except (Branch.DoesNotExist, ValueError):
                pass
    
    # If we have a branch, add currency info to context
    if branch:
        context['branch_currency_symbol'] = branch.currency_symbol
        context['branch_currency_code'] = branch.currency_code
    else:
        # Fallback to default
        context['branch_currency_symbol'] = '$'
        context['branch_currency_code'] = 'USD'
    
    return context
