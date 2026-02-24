"""
Скрипт для отключения 2FA у пользователя (восстановление доступа)
Использование: python scripts/disable_2fa_for_user.py <username>
"""
import sys
import os

# Добавляем корневую директорию в path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.models import User

def disable_2fa(username):
    """Отключает 2FA для указанного пользователя"""
    app = create_app('development')
    
    with app.app_context():
        db = app.db
        user = db.session.query(User).filter_by(username=username).first()
        
        if not user:
            print(f"❌ Пользователь '{username}' не найден")
            return False
        
        if not user.two_factor_enabled:
            print(f"ℹ️  У пользователя '{username}' 2FA уже отключена")
            return True
        
        user.two_factor_enabled = False
        user.two_factor_secret = None
        db.session.commit()
        
        print(f"✅ 2FA успешно отключена для пользователя '{username}'")
        print(f"   Теперь можно войти без кода из аутентификатора")
        return True

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Использование: python scripts/disable_2fa_for_user.py <username>")
        print("Пример: python scripts/disable_2fa_for_user.py admin")
        sys.exit(1)
    
    username = sys.argv[1]
    disable_2fa(username)
