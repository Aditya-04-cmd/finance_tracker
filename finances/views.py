from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from  django.utils import timezone
from datetime import datetime, timedelta
from matplotlib import pyplot as plt, use
import io
import base64
import pandas as pd
from decimal import Decimal

from .models import Category, Transaction
from .forms import CategoryForm, TransactionForm, DateRangeFilterForm

use('Agg')

#Dashboard view
@login_required
def dashboard(request):
    today = timezone.now()
    month_start = today.replace(day=1)
    last_month_start = (month_start-timedelta(days=1)).replace(day=1)

    # Get transactions for current month
    current_month_expenses = Transaction.objects.filter(
        user=request.user,
        transaction_type='expense',
        date__gte=month_start,
        date__lte=today
    ).aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
    
    current_month_income = Transaction.objects.filter(
        user=request.user,
        transaction_type='income',
        date__gte=month_start,
        date__lte=today
    ).aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')

    # Get transactions for last month
    last_month_expenses = Transaction.objects.filter(
        user=request.user,
        transaction_type='expense',
        date__gte=last_month_start,
        date__lt=month_start
    ).aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
    
    last_month_income = Transaction.objects.filter(
        user=request.user,
        transaction_type='income',
        date__gte=last_month_start,
        date__lt=month_start
    ).aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
    
    # Calculate balance
    current_balance = current_month_income - current_month_expenses
    last_month_balance = last_month_income - last_month_expenses

    # Recent transactions
    recent_transactions = Transaction.objects.filter(user=request.user).order_by('-date')[:5]
    
    # Generate category charts
    expense_by_category = Transaction.objects.filter(
        user=request.user,
        transaction_type='expense',
        date__gte=month_start,
        date__lte=today
    ).values('category__name').annotate(total=Sum('amount')).order_by('-total')

    # Create expense pie chart
    if expense_by_category:
        plt.figure(figsize=(8, 6))
        plt.pie([item['total'] for item in expense_by_category], 
                labels=[item['category__name'] for item in expense_by_category],
                autopct='%1.1f%%')
        plt.title('Expenses by Category (Current Month)')
        
        # Save plot to a temporary buffer
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        expense_chart = base64.b64encode(buf.getvalue()).decode('utf-8')
        plt.close()
    else:
        expense_chart = None
    
    context = {
        'current_month_expenses': current_month_expenses,
        'current_month_income': current_month_income,
        'last_month_expenses': last_month_expenses,
        'last_month_income': last_month_income,
        'current_balance': current_balance,
        'last_month_balance': last_month_balance,
        'recent_transactions': recent_transactions,
        'expense_chart': expense_chart,
    }
    
    return render(request, 'finances/dashboard.html', context)

#Transaction view
@login_required
def transaction_list(request):
    form = DateRangeFilterForm(request.GET, user=request.user)
    transactions = Transaction.objects.filter(user=request.user)
    
    if form.is_valid():
        start_date = form.cleaned_data.get('start_date')
        end_date = form.cleaned_data.get('end_date')
        category = form.cleaned_data.get('category')
        transaction_type = form.cleaned_data.get('transaction_type')
        
        if start_date:
            transactions = transactions.filter(date__gte=start_date)
        if end_date:
            transactions = transactions.filter(date__lte=end_date)
        if category:
            transactions = transactions.filter(category=category)
        if transaction_type:
            transactions = transactions.filter(transaction_type=transaction_type)
    
    total_expenses = transactions.filter(transaction_type='expense').aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
    total_income = transactions.filter(transaction_type='income').aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
    balance = total_income - total_expenses
    
    context = {
        'transactions': transactions,
        'form': form,
        'total_expenses': total_expenses,
        'total_income': total_income,
        'balance': balance,
    }
    
    return render(request, 'finances/transaction_list.html', context)

@login_required
def add_transaction(request):
    if request.method == 'POST':
        form = TransactionForm(request.POST, user=request.user)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.user = request.user
            transaction.save()
            messages.success(request, 'Transaction added successfully!')
            return redirect('transaction_list')
    else:
        form = TransactionForm(user=request.user)
    
    return render(request, 'finances/transaction_form.html', {'form': form, 'title': 'Add Transaction'})

@login_required
def edit_transaction(request, pk):
    transaction = get_object_or_404(Transaction, pk=pk, user=request.user)
    
    if request.method == 'POST':
        form = TransactionForm(request.POST, instance=transaction, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Transaction updated successfully!')
            return redirect('transaction_list')
    else:
        form = TransactionForm(instance=transaction, user=request.user)
    
    return render(request, 'finances/transaction_form.html', {'form': form, 'title': 'Edit Transaction'})

@login_required
def delete_transaction(request, pk):
    transaction = get_object_or_404(Transaction, pk=pk, user=request.user)
    
    if request.method == 'POST':
        transaction.delete()
        messages.success(request, 'Transaction deleted successfully!')
        return redirect('transaction_list')
    
    return render(request, 'finances/confirm_delete.html', {'object': transaction})

#Category views
@login_required
def category_list(request):
    categories = Category.objects.filter(user=request.user)
    return render(request, 'finances/category_list.html', {'categories': categories})

@login_required
def add_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.save(commit=False)
            category.user = request.user
            category.save()
            messages.success(request, 'Category added successfully!')
            return redirect('category_list')
    else:
        form = CategoryForm()
    
    return render(request, 'finances/category_form.html', {'form': form, 'title': 'Add Category'})

@login_required
def edit_category(request, pk):
    category = get_object_or_404(Category, pk=pk, user=request.user)
    
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category updated successfully!')
            return redirect('category_list')
    else:
        form = CategoryForm(instance=category)
    
    return render(request, 'finances/category_form.html', {'form': form, 'title': 'Edit Category'})

@login_required
def delete_category(request, pk):
    category = get_object_or_404(Category, pk=pk, user=request.user)
    
    if request.method == 'POST':
        category.delete()
        messages.success(request, 'Category deleted successfully!')
        return redirect('category_list')
    
    return render(request, 'finances/confirm_delete.html', {'object': category})

#Reports view
@login_required
def reports(request):
    form = DateRangeFilterForm(request.GET, user=request.user)
    transactions = Transaction.objects.filter(user=request.user)
    
    if form.is_valid():
        start_date = form.cleaned_data.get('start_date')
        end_date = form.cleaned_data.get('end_date')
        category = form.cleaned_data.get('category')
        transaction_type = form.cleaned_data.get('transaction_type')
        
        if start_date:
            transactions = transactions.filter(date__gte=start_date)
        if end_date:
            transactions = transactions.filter(date__lte=end_date)
        if category:
            transactions = transactions.filter(category=category)
        if transaction_type:
            transactions = transactions.filter(transaction_type=transaction_type)
    
    # Generate charts
    charts = {}
    
    # Expenses by category chart
    expense_by_category = transactions.filter(
        transaction_type='expense'
    ).values('category__name').annotate(total=Sum('amount')).order_by('-total')
    
    if expense_by_category:
        plt.figure(figsize=(10, 6))
        plt.pie([item['total'] for item in expense_by_category], 
                labels=[item['category__name'] for item in expense_by_category],
                autopct='%1.1f%%')
        plt.title('Expenses by Category')
        
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        charts['expense_category_chart'] = base64.b64encode(buf.getvalue()).decode('utf-8')
        plt.close()
    
    # Monthly trend chart
    if transactions:
        # Convert to pandas for easier date grouping
        data = pd.DataFrame(list(transactions.values('date', 'amount', 'transaction_type')))
        
        # Convert date column to datetime
        data['date'] = pd.to_datetime(data['date'])
        
        # Extract month and year
        data['month_year'] = data['date'].dt.strftime('%Y-%m')
        
        # Group by month and transaction type
        monthly_data = data.groupby(['month_year', 'transaction_type'])['amount'].sum().unstack()
        
        if not monthly_data.empty:
            plt.figure(figsize=(12, 6))
            
            if 'expense' in monthly_data.columns:
                plt.bar(monthly_data.index, monthly_data['expense'], color='red', alpha=0.7, label='Expenses')
            
            if 'income' in monthly_data.columns:
                plt.bar(monthly_data.index, monthly_data['income'], color='green', alpha=0.7, label='Income')
            
            plt.title('Monthly Income and Expenses')
            plt.xlabel('Month')
            plt.ylabel('Amount')
            plt.xticks(rotation=45)
            plt.legend()
            plt.tight_layout()
            
            buf = io.BytesIO()
            plt.savefig(buf, format='png')
            buf.seek(0)
            charts['monthly_trend_chart'] = base64.b64encode(buf.getvalue()).decode('utf-8')
            plt.close()
    
    # Calculate summary statistics
    total_expenses = transactions.filter(transaction_type='expense').aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
    total_income = transactions.filter(transaction_type='income').aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
    balance = total_income - total_expenses
    
    context = {
        'form': form,
        'total_expenses': total_expenses,
        'total_income': total_income,
        'balance': balance,
        'charts': charts,
    }
    
    return render(request, 'finances/reports.html', context)

#Export data
@login_required
def export_data(request):
    transactions = Transaction.objects.filter(user=request.user)
    
    # Filter data if form is submitted
    form = DateRangeFilterForm(request.GET, user=request.user)
    if form.is_valid():
        start_date = form.cleaned_data.get('start_date')
        end_date = form.cleaned_data.get('end_date')
        category = form.cleaned_data.get('category')
        transaction_type = form.cleaned_data.get('transaction_type')
        
        if start_date:
            transactions = transactions.filter(date__gte=start_date)
        if end_date:
            transactions = transactions.filter(date__lte=end_date)
        if category:
            transactions = transactions.filter(category=category)
        if transaction_type:
            transactions = transactions.filter(transaction_type=transaction_type)
    
    # Convert to pandas DataFrame for easier export
    data = pd.DataFrame(list(transactions.values(
        'description', 'amount', 'date', 'category__name', 'transaction_type'
    )))
    
    # Rename columns for better readability
    if not data.empty:
        data = data.rename(columns={
            'category__name': 'category',
            'transaction_type': 'type'
        })
    
    # Create response with CSV file
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="finance_data.csv"'
    
    if not data.empty:
        data.to_csv(response, index=False)
    else:
        response.write('No data available for export')
    
    return response