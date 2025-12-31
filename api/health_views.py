"""
Health Monitoring API Views

Provides endpoints for monitoring sync health across branches.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from accounts.models import Branch
from django.utils import timezone
from datetime import timedelta


class SyncHealthViewSet(viewsets.ViewSet):
    """
    ViewSet for monitoring sync health across branches.
    """
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'], url_path='branches')
    def branches(self, request):
        """
        Get sync health status for all branches.
        """
        # Get user's tenant
        user_profile = request.user.profiles.filter(tenant=request.tenant).first()
        if not user_profile:
            return Response({'error': 'User profile not found'}, status=status.HTTP_403_FORBIDDEN)
        
        # Get all branches for this tenant
        branches = Branch.objects.filter(tenant=request.tenant).order_by('name')
        
        branch_data = []
        for branch in branches:
            # Calculate sync lag
            sync_lag = None
            if branch.last_sync_at:
                sync_lag = (timezone.now() - branch.last_sync_at).total_seconds()
            
            branch_data.append({
                'id': str(branch.id),
                'name': branch.name,
                'sync_status': branch.sync_status,
                'last_sync_at': branch.last_sync_at.isoformat() if branch.last_sync_at else None,
                'sync_lag_seconds': sync_lag,
                'pending_sync_count': branch.pending_sync_count,
                'sync_error_message': branch.sync_error_message,
                'branch_type': branch.branch_type,
            })
        
        return Response({
            'branches': branch_data,
            'total_count': len(branch_data),
            'healthy_count': len([b for b in branch_data if b['sync_status'] == 'healthy']),
            'warning_count': len([b for b in branch_data if b['sync_status'] == 'warning']),
            'error_count': len([b for b in branch_data if b['sync_status'] == 'error']),
        })
    
    @action(detail=False, methods=['get'], url_path='branches/(?P<branch_id>[^/.]+)')
    def branch_detail(self, request, branch_id=None):
        """
        Get detailed sync health for a specific branch.
        """
        try:
            branch = Branch.objects.get(id=branch_id, tenant=request.tenant)
        except Branch.DoesNotExist:
            return Response({'error': 'Branch not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Calculate sync lag
        sync_lag = None
        if branch.last_sync_at:
            sync_lag = (timezone.now() - branch.last_sync_at).total_seconds()
        
        return Response({
            'id': str(branch.id),
            'name': branch.name,
            'sync_status': branch.sync_status,
            'last_sync_at': branch.last_sync_at.isoformat() if branch.last_sync_at else None,
            'sync_lag_seconds': sync_lag,
            'pending_sync_count': branch.pending_sync_count,
            'sync_error_message': branch.sync_error_message,
            'branch_type': branch.branch_type,
            'address': branch.address,
            'phone': branch.phone,
        })
    
    @action(detail=False, methods=['get'], url_path='metrics')
    def metrics(self, request):
        """
        Get system-wide sync metrics.
        """
        branches = Branch.objects.filter(tenant=request.tenant)
        
        # Calculate metrics
        total_branches = branches.count()
        healthy_branches = branches.filter(sync_status='healthy').count()
        warning_branches = branches.filter(sync_status='warning').count()
        error_branches = branches.filter(sync_status='error').count()
        
        # Average sync lag
        recent_syncs = branches.filter(last_sync_at__isnull=False)
        avg_sync_lag = 0
        if recent_syncs.exists():
            total_lag = sum([
                (timezone.now() - b.last_sync_at).total_seconds() 
                for b in recent_syncs
            ])
            avg_sync_lag = total_lag / recent_syncs.count()
        
        # Total pending syncs
        total_pending = sum([b.pending_sync_count for b in branches])
        
        return Response({
            'total_branches': total_branches,
            'healthy_branches': healthy_branches,
            'warning_branches': warning_branches,
            'error_branches': error_branches,
            'health_percentage': (healthy_branches / total_branches * 100) if total_branches > 0 else 0,
            'average_sync_lag_seconds': avg_sync_lag,
            'total_pending_syncs': total_pending,
            'timestamp': timezone.now().isoformat(),
        })
