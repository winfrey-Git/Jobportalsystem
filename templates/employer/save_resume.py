{% extends 'base.html' %}

{% block content %}
<div class="container mt-4">
    <h2>Resume Saved Successfully</h2>
    <p><a href="{% url 'view_resume' resume.id %}" class="btn btn-primary">Back to Resume</a></p>
</div>
{% endblock %}
