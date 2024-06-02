# tools for the agents
class ResearchTools:
    @staticmethod
    def tools():
        return ['read_repo_files', 'query_rules_file']
    
# tools to push comments to the PR
class FeedbackTools:
    @staticmethod
    def tools():
        return ['push_comment']