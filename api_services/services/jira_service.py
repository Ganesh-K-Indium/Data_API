"""
JIRA Service - Business logic for JIRA operations
"""
from typing import List, Dict, Any, Optional

try:
    from ..models import (
        FileInfo,
        ListFilesResponse,
        SearchResponse,
        JiraProject
    )
except ImportError:
    from models import (
        FileInfo,
        ListFilesResponse,
        SearchResponse,
        JiraProject
    )


class JiraService:
    """Service layer for JIRA operations"""
    
    def __init__(self, client):
        self.client = client
        self.jira = client.jira_client
    
    def list_projects(self) -> List[JiraProject]:
        """List all accessible JIRA projects"""
        try:
            projects = self.jira.projects()
            result = []
            for p in projects:
                result.append(JiraProject(
                    key=str(p.key),
                    name=str(p.name),
                    id=str(p.id),
                    project_type=str(getattr(p, 'projectTypeKey', 'unknown'))
                ))
            return result
        except AttributeError as e:
            # Handle missing jira_client
            raise Exception(f"JIRA client not properly initialized: {str(e)}")
        except Exception as e:
            raise Exception(f"Failed to list projects: {str(e)}")
    
    def list_issues(
        self,
        project_key: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> ListFilesResponse:
        """List issues from JIRA"""
        try:
            jql_parts = []
            if project_key:
                jql_parts.append(f"project={project_key}")
            
            jql = " AND ".join(jql_parts) if jql_parts else ""
            
            issues = self.jira.search_issues(
                jql,
                startAt=offset,
                maxResults=limit,
                fields='summary,issuetype,status,priority,assignee,created,updated,project'
            )
            
            files = []
            for issue in issues:
                files.append(FileInfo(
                    id=issue.key,
                    name=f"{issue.key}: {issue.fields.summary}",
                    type='issue',
                    created_date=issue.fields.created,
                    modified_date=issue.fields.updated,
                    url=f"{self.jira._options['server']}/browse/{issue.key}",
                    metadata={
                        'issue_key': issue.key,
                        'project_key': issue.fields.project.key,
                        'issue_type': issue.fields.issuetype.name,
                        'status': issue.fields.status.name,
                        'priority': issue.fields.priority.name if issue.fields.priority else None,
                        'assignee': issue.fields.assignee.displayName if issue.fields.assignee else None
                    }
                ))
            
            return ListFilesResponse(
                success=True,
                files=files,
                total_count=issues.total,
                has_more=(offset + len(files)) < issues.total
            )
        
        except Exception as e:
            return ListFilesResponse(
                success=False,
                files=[],
                total_count=0,
                message=f"Failed to list issues: {str(e)}"
            )
    
    def search_issues(
        self,
        query: str,
        project_key: Optional[str] = None,
        limit: int = 50
    ) -> SearchResponse:
        """Search JIRA issues"""
        try:
            jql_parts = [f'text ~ "{query}"']
            if project_key:
                jql_parts.append(f"project={project_key}")
            
            jql = " AND ".join(jql_parts)
            
            issues = self.jira.search_issues(
                jql,
                maxResults=limit,
                fields='summary,issuetype,status,priority,created,updated,project'
            )
            
            files = []
            for issue in issues:
                files.append(FileInfo(
                    id=issue.key,
                    name=f"{issue.key}: {issue.fields.summary}",
                    type='issue',
                    created_date=issue.fields.created,
                    modified_date=issue.fields.updated,
                    url=f"{self.jira._options['server']}/browse/{issue.key}",
                    metadata={
                        'issue_key': issue.key,
                        'project_key': issue.fields.project.key,
                        'issue_type': issue.fields.issuetype.name,
                        'status': issue.fields.status.name
                    }
                ))
            
            return SearchResponse(
                success=True,
                results=files,
                total_count=issues.total
            )
        
        except Exception as e:
            return SearchResponse(
                success=False,
                results=[],
                total_count=0,
                message=f"Search failed: {str(e)}"
            )
    
    def get_issue_details(self, issue_key: str) -> Dict[str, Any]:
        """Get detailed information about a specific issue"""
        try:
            issue = self.jira.issue(issue_key)
            
            return {
                'key': issue.key,
                'summary': issue.fields.summary,
                'description': issue.fields.description or '',
                'issue_type': issue.fields.issuetype.name,
                'status': issue.fields.status.name,
                'priority': issue.fields.priority.name if issue.fields.priority else None,
                'assignee': issue.fields.assignee.displayName if issue.fields.assignee else None,
                'reporter': issue.fields.reporter.displayName if issue.fields.reporter else None,
                'created': issue.fields.created,
                'updated': issue.fields.updated,
                'project_key': issue.fields.project.key,
                'url': f"{self.jira._options['server']}/browse/{issue.key}"
            }
        except Exception as e:
            raise Exception(f"Failed to get issue details: {str(e)}")
