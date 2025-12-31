from django.contrib import messages
from django.shortcuts import render, redirect
from django.db import connection
from django.http import HttpResponse
import csv
from datetime import datetime

def bulk_export_tenant_data(modeladmin, request, queryset):
    """Export key metrics for selected tenants to CSV"""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="tenant_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Tenant Name', 'Subdomain', 'Branches', 'Products', 'Orders', 'Revenue', 'Created On'])
    
    for tenant in queryset:
        try:
            # Get metrics from tenant schema
            with connection.cursor() as cursor:
                cursor.execute(f"SET search_path TO {tenant.schema_name}")
                
                # Get counts
                cursor.execute("SELECT COUNT(*) FROM accounts_branch")
                branches = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM main_product")
                products = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM main_order")
                orders = cursor.fetchone()[0]
                
                cursor.execute("SELECT COALESCE(SUM(total_amount), 0) FROM main_order WHERE status = 'completed'")
                revenue = cursor.fetchone()[0]
                
                cursor.execute("SET search_path TO public")
            
            writer.writerow([
                tenant.name,
                tenant.subdomain,
                branches,
                products,
                orders,
                f"${float(revenue):,.2f}",
                tenant.created_on.strftime('%Y-%m-%d')
            ])
        except Exception as e:
            writer.writerow([tenant.name, tenant.subdomain, 'Error', 'Error', 'Error', 'Error', tenant.created_on.strftime('%Y-%m-%d')])
    
    return response

bulk_export_tenant_data.short_description = "Export tenant data to CSV"


def bulk_send_notification(modeladmin, request, queryset):
    """Send notification to selected tenants"""
    if 'apply' in request.POST:
        # Process the form
        message_title = request.POST.get('message_title')
        message_body = request.POST.get('message_body')
        
        count = 0
        for tenant in queryset:
            try:
                # Switch to tenant schema and create notification
                with connection.cursor() as cursor:
                    cursor.execute(f"SET search_path TO {tenant.schema_name}")
                    
                    # Get all users in this tenant
                    cursor.execute("SELECT id FROM accounts_userprofile")
                    user_profiles = cursor.fetchall()
                    
                    # Create notification for each user
                    for (profile_id,) in user_profiles:
                        cursor.execute("""
                            INSERT INTO notifications_notification (id, user_id, title, message, is_read, created_at)
                            VALUES (gen_random_uuid(), %s, %s, %s, false, NOW())
                        """, [profile_id, message_title, message_body])
                    
                    cursor.execute("SET search_path TO public")
                    count += 1
            except Exception as e:
                messages.error(request, f"Error sending to {tenant.name}: {str(e)}")
        
        messages.success(request, f"Notification sent to {count} tenant(s)")
        return redirect(request.get_full_path())
    
    # Show the form
    return render(request, 'admin/bulk_notification_form.html', {
        'tenants': queryset,
        'action': 'bulk_send_notification',
    })

bulk_send_notification.short_description = "Send notification to selected tenants"


def bulk_generate_report(modeladmin, request, queryset):
    """Generate comparison report for selected tenants"""
    report_data = []
    
    for tenant in queryset:
        try:
            with connection.cursor() as cursor:
                cursor.execute(f"SET search_path TO {tenant.schema_name}")
                
                # Get comprehensive metrics
                cursor.execute("SELECT COUNT(*) FROM accounts_branch")
                branches = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM main_product")
                products = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM main_order")
                total_orders = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM main_order WHERE status = 'completed'")
                completed_orders = cursor.fetchone()[0]
                
                cursor.execute("SELECT COALESCE(SUM(total_amount), 0) FROM main_order WHERE status = 'completed'")
                revenue = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM main_customer")
                customers = cursor.fetchone()[0]
                
                cursor.execute("SET search_path TO public")
                
                report_data.append({
                    'tenant': tenant,
                    'branches': branches,
                    'products': products,
                    'total_orders': total_orders,
                    'completed_orders': completed_orders,
                    'revenue': float(revenue),
                    'customers': customers,
                    'completion_rate': (completed_orders / total_orders * 100) if total_orders > 0 else 0,
                })
        except Exception as e:
            report_data.append({
                'tenant': tenant,
                'error': str(e)
            })
    
    return render(request, 'admin/bulk_report.html', {
        'report_data': report_data,
        'generated_at': datetime.now(),
    })

bulk_generate_report.short_description = "Generate comparison report"
