function getISOWeekInfo(date) {
    const tempDate = new Date(date);
    tempDate.setHours(0, 0, 0, 0);
    tempDate.setDate(tempDate.getDate() + 4 - (tempDate.getDay() || 7));
    const yearStart = new Date(tempDate.getFullYear(), 0, 1);
    const weekNo = Math.ceil((((tempDate - yearStart) / 86400000) + 1) / 7);
    return weekNo
}

function showDateFields(logType, date) {
    const ddate = new Date(date);
    const year = ddate.getFullYear();
    const month = ddate.getMonth() + 1;
    const day = ddate.getDate();
    const week = getISOWeekInfo(date);

    document.querySelectorAll('.myTaskForm').forEach(function(element) {
        element.style.display = 'none';
    });

    document.querySelectorAll('.myTaskForm input').forEach(function(element) {
        element.value = '';
    });

    if (logType === 'daily') {
        document.getElementById('date-daily').style.display = 'flex';
        document.getElementById('day_year').value = year;
        document.getElementById('day_month').value = month;
        document.getElementById('day_number').value = day;
    } else if (logType === 'weekly') {
        document.getElementById('date-weekly').style.display = 'flex';
        document.getElementById('week_year').value = year;
        document.getElementById('week_number').value = week;
    } else if (logType === 'monthly') {
        document.getElementById('date-monthly').style.display = 'flex';
        document.getElementById('month_year').value = year;
        document.getElementById('month_number').value = month;
    } else if (logType === 'yearly') {
        document.getElementById('date-yearly').style.display = 'flex';
        document.getElementById('yearly_year').value = year;
    }
}


function editLog(logId, logType) {
    document.getElementById('log-' + logId + '-view').style.display = 'none';
    document.getElementById('log-' + logId + '-edit').style.display = 'block';
}

function cancelEdit(logId) {
    document.getElementById('log-' + logId + '-edit').style.display = 'none';
    document.getElementById('log-' + logId + '-view').style.display = 'flex';
}


function submitForm(event, formId) {
    event.preventDefault();
    var form = document.getElementById(formId);
    form.submit();
}

