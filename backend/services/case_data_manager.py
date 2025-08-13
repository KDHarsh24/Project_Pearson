class CaseDataManager:
    def __init__(self):
        pass
    def create_case_data(self, *args, **kwargs):
        return {"case_id": "test", "json_file": "test.json"}
    def create_diagram(self, *args, **kwargs):
        return None
    def get_all_cases(self):
        return []
    def get_case_by_id(self, case_id):
        return None
    def get_diagram_path(self, case_id):
        return None
