from rest_framework import permissions



class OnlySuperUser(permissions.BasePermission):
    '''Permissão que permite acesso apenas a superusuários.'''
    def has_permission(self, request, view) -> bool:
        return request.user and request.user.is_superuser
    
class IsInGroup(permissions.BasePermission):
    '''Permissão que permite acesso apenas a grupos específicos.'''
    def has_permission(self, request, view) -> bool:
        required_groups = getattr(view, 'required_groups', [])

        if not required_groups:
            return True
        
        return request.user.groups.filter(name__in=required_groups).exists() or request.user.is_superuser

    
class AlunoOnlyRead(permissions.BasePermission):
    '''Permissão para views em que os alunos tenham permissão apenas de leitura.'''
    def has_permission(self, request, view) -> bool:
        user = request.user

        if user.groups.filter(name='aluno').exists():
            if request.method == 'GET':
                return True
            return False
            
        return True