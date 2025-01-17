class SessionManager:
    @staticmethod
    def add_projects_to_session(request, projects):
        request.session['selected_projects'] = projects