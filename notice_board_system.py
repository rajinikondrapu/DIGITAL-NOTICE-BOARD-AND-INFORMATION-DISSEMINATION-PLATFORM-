"""
Digital Notice Board and Information Dissemination Platform
Core system module for notice management, personalization, and notification delivery
"""

import sqlite3
import json
import hashlib
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
import uuid
from enum import Enum


class UserRole(Enum):
    """User role enumeration"""
    STUDENT = "student"
    FACULTY = "faculty"
    ADMIN = "admin"
    STAFF = "staff"


class NoticePriority(Enum):
    """Notice priority levels"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    URGENT = 4


class NoticeCategory(Enum):
    """Notice categories"""
    ACADEMICS = "academics"
    EXAMINATIONS = "examinations"
    EVENTS = "events"
    PLACEMENTS = "placements"
    SCHOLARSHIPS = "scholarships"
    ADMINISTRATIVE = "administrative"
    GENERAL = "general"


class User:
    """Represents a user in the system"""
    
    def __init__(self, user_id: str, name: str, email: str, role: UserRole, 
                 department: str, academic_year: int = 1):
        self.user_id = user_id
        self.name = name
        self.email = email
        self.role = role
        self.department = department
        self.academic_year = academic_year
        self.preferences = {}
        self.notification_channels = ["web", "email"]
        
    def to_dict(self) -> Dict:
        """Convert user to dictionary"""
        return {
            "user_id": self.user_id,
            "name": self.name,
            "email": self.email,
            "role": self.role.value,
            "department": self.department,
            "academic_year": self.academic_year,
            "preferences": self.preferences,
            "notification_channels": self.notification_channels
        }


class Notice:
    """Represents a notice in the system"""
    
    def __init__(self, notice_id: str, title: str, content: str, 
                 category: NoticeCategory, priority: NoticePriority,
                 created_by: str, created_at: datetime = None):
        self.notice_id = notice_id
        self.title = title
        self.content = content
        self.category = category
        self.priority = priority
        self.created_by = created_by
        self.created_at = created_at or datetime.now()
        self.expiry_date = self.created_at + timedelta(days=30)
        self.attachments = []
        self.target_departments = []
        self.target_academic_years = []
        self.target_roles = []
        self.view_count = 0
        self.engagement_score = 0.0
        
    def to_dict(self) -> Dict:
        """Convert notice to dictionary"""
        return {
            "notice_id": self.notice_id,
            "title": self.title,
            "content": self.content,
            "category": self.category.value,
            "priority": self.priority.value,
            "created_by": self.created_by,
            "created_at": self.created_at.isoformat(),
            "expiry_date": self.expiry_date.isoformat(),
            "attachments": self.attachments,
            "target_departments": self.target_departments,
            "target_academic_years": self.target_academic_years,
            "target_roles": self.target_roles,
            "view_count": self.view_count,
            "engagement_score": self.engagement_score
        }


class PersonalizationEngine:
    """Engine for personalizing notice delivery based on user preferences"""
    
    def __init__(self):
        self.user_preferences = {}
        self.category_weights = {}
        
    def should_notify_user(self, user: User, notice: Notice) -> bool:
        """Determine if a user should be notified about a notice"""
        
        # Check role-based targeting
        if notice.target_roles and user.role.value not in notice.target_roles:
            return False
            
        # Check department-based targeting
        if notice.target_departments and user.department not in notice.target_departments:
            return False
            
        # Check academic year targeting
        if notice.target_academic_years and user.academic_year not in notice.target_academic_years:
            return False
            
        # Check user preferences
        if user.user_id in self.user_preferences:
            prefs = self.user_preferences[user.user_id]
            if "excluded_categories" in prefs:
                if notice.category.value in prefs["excluded_categories"]:
                    return False
            if "preferred_categories" in prefs:
                if notice.category.value not in prefs["preferred_categories"]:
                    return False
                    
        return True
    
    def calculate_relevance_score(self, user: User, notice: Notice) -> float:
        """Calculate relevance score for a notice to a user"""
        
        score = 0.0
        
        # Category preference score
        if user.user_id in self.user_preferences:
            prefs = self.user_preferences[user.user_id]
            if "category_interests" in prefs:
                if notice.category.value in prefs["category_interests"]:
                    score += 0.4
                    
        # Role-based score
        if notice.target_roles and user.role.value in notice.target_roles:
            score += 0.3
            
        # Department-based score
        if notice.target_departments and user.department in notice.target_departments:
            score += 0.2
            
        # Priority-based score
        score += (notice.priority.value / 4.0) * 0.1
        
        return min(score, 1.0)


class NotificationEngine:
    """Engine for delivering notifications through multiple channels"""
    
    def __init__(self):
        self.notifications_sent = 0
        self.notifications_failed = 0
        self.delivery_times = []
        
    def send_notification(self, user: User, notice: Notice, channels: List[str] = None) -> bool:
        """Send notification to user through specified channels"""
        
        if channels is None:
            channels = user.notification_channels
            
        start_time = datetime.now()
        success = True
        
        for channel in channels:
            if channel == "web":
                success &= self._send_web_notification(user, notice)
            elif channel == "email":
                success &= self._send_email_notification(user, notice)
            elif channel == "sms":
                success &= self._send_sms_notification(user, notice)
                
        delivery_time = (datetime.now() - start_time).total_seconds()
        self.delivery_times.append(delivery_time)
        
        if success:
            self.notifications_sent += 1
        else:
            self.notifications_failed += 1
            
        return success
    
    def _send_web_notification(self, user: User, notice: Notice) -> bool:
        """Send web push notification"""
        try:
            # Simulate web notification delivery
            return True
        except Exception:
            return False
    
    def _send_email_notification(self, user: User, notice: Notice) -> bool:
        """Send email notification"""
        try:
            # Simulate email delivery
            return True
        except Exception:
            return False
    
    def _send_sms_notification(self, user: User, notice: Notice) -> bool:
        """Send SMS notification"""
        try:
            # Simulate SMS delivery
            return True
        except Exception:
            return False
    
    def get_average_delivery_time(self) -> float:
        """Get average notification delivery time"""
        if not self.delivery_times:
            return 0.0
        return sum(self.delivery_times) / len(self.delivery_times)
    
    def get_delivery_success_rate(self) -> float:
        """Get notification delivery success rate"""
        total = self.notifications_sent + self.notifications_failed
        if total == 0:
            return 0.0
        return (self.notifications_sent / total) * 100


class EngagementTracker:
    """Tracks user engagement with notices"""
    
    def __init__(self):
        self.engagement_data = {}
        self.view_counts = {}
        self.click_counts = {}
        
    def record_view(self, user_id: str, notice_id: str) -> None:
        """Record notice view"""
        key = f"{user_id}:{notice_id}"
        if key not in self.engagement_data:
            self.engagement_data[key] = {
                "views": 0,
                "clicks": 0,
                "first_viewed": datetime.now(),
                "last_viewed": datetime.now()
            }
        self.engagement_data[key]["views"] += 1
        self.engagement_data[key]["last_viewed"] = datetime.now()
        
        if notice_id not in self.view_counts:
            self.view_counts[notice_id] = 0
        self.view_counts[notice_id] += 1
    
    def record_click(self, user_id: str, notice_id: str) -> None:
        """Record notice click"""
        key = f"{user_id}:{notice_id}"
        if key not in self.engagement_data:
            self.engagement_data[key] = {
                "views": 0,
                "clicks": 0,
                "first_viewed": datetime.now(),
                "last_viewed": datetime.now()
            }
        self.engagement_data[key]["clicks"] += 1
        
        if notice_id not in self.click_counts:
            self.click_counts[notice_id] = 0
        self.click_counts[notice_id] += 1
    
    def get_engagement_rate(self, notice_id: str) -> float:
        """Get engagement rate for a notice"""
        if notice_id not in self.view_counts:
            return 0.0
        views = self.view_counts.get(notice_id, 0)
        clicks = self.click_counts.get(notice_id, 0)
        if views == 0:
            return 0.0
        return (clicks / views) * 100


class NoticeBoardSystem:
    """Main notice board system"""
    
    def __init__(self, db_path: str = "notice_board.db"):
        self.db_path = db_path
        self.notices = {}
        self.users = {}
        self.personalization_engine = PersonalizationEngine()
        self.notification_engine = NotificationEngine()
        self.engagement_tracker = EngagementTracker()
        self._init_database()
        
    def _init_database(self) -> None:
        """Initialize database tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                role TEXT NOT NULL,
                department TEXT NOT NULL,
                academic_year INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS notices (
                notice_id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                category TEXT NOT NULL,
                priority INTEGER NOT NULL,
                created_by TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expiry_date TIMESTAMP,
                view_count INTEGER DEFAULT 0,
                engagement_score REAL DEFAULT 0.0
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS notice_targeting (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                notice_id TEXT NOT NULL,
                target_type TEXT NOT NULL,
                target_value TEXT NOT NULL,
                FOREIGN KEY (notice_id) REFERENCES notices(notice_id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_notifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                notice_id TEXT NOT NULL,
                delivered BOOLEAN DEFAULT 0,
                viewed BOOLEAN DEFAULT 0,
                clicked BOOLEAN DEFAULT 0,
                delivered_at TIMESTAMP,
                viewed_at TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id),
                FOREIGN KEY (notice_id) REFERENCES notices(notice_id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS engagement_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                notice_id TEXT NOT NULL,
                views INTEGER DEFAULT 0,
                clicks INTEGER DEFAULT 0,
                first_viewed TIMESTAMP,
                last_viewed TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id),
                FOREIGN KEY (notice_id) REFERENCES notices(notice_id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_user(self, user: User) -> bool:
        """Add user to system"""
        try:
            self.users[user.user_id] = user
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO users (user_id, name, email, role, department, academic_year)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (user.user_id, user.name, user.email, user.role.value, 
                  user.department, user.academic_year))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error adding user: {e}")
            return False
    
    def publish_notice(self, notice: Notice) -> bool:
        """Publish a notice"""
        try:
            self.notices[notice.notice_id] = notice
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO notices (notice_id, title, content, category, priority, 
                                    created_by, created_at, expiry_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (notice.notice_id, notice.title, notice.content, notice.category.value,
                  notice.priority.value, notice.created_by, notice.created_at.isoformat(),
                  notice.expiry_date.isoformat()))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error publishing notice: {e}")
            return False
    
    def set_notice_targeting(self, notice_id: str, departments: List[str] = None,
                            academic_years: List[int] = None, 
                            roles: List[str] = None) -> bool:
        """Set targeting for a notice"""
        try:
            if notice_id not in self.notices:
                return False
                
            notice = self.notices[notice_id]
            if departments:
                notice.target_departments = departments
            if academic_years:
                notice.target_academic_years = academic_years
            if roles:
                notice.target_roles = roles
                
            return True
        except Exception as e:
            print(f"Error setting notice targeting: {e}")
            return False
    
    def distribute_notice(self, notice_id: str) -> Dict:
        """Distribute notice to eligible users"""
        if notice_id not in self.notices:
            return {"success": False, "message": "Notice not found"}
            
        notice = self.notices[notice_id]
        distribution_stats = {
            "total_users": 0,
            "notified_users": 0,
            "failed_deliveries": 0,
            "average_delivery_time": 0.0
        }
        
        for user_id, user in self.users.items():
            distribution_stats["total_users"] += 1
            
            # Check if user should be notified
            if self.personalization_engine.should_notify_user(user, notice):
                success = self.notification_engine.send_notification(user, notice)
                if success:
                    distribution_stats["notified_users"] += 1
                else:
                    distribution_stats["failed_deliveries"] += 1
        
        distribution_stats["average_delivery_time"] = \
            self.notification_engine.get_average_delivery_time()
            
        return {
            "success": True,
            "notice_id": notice_id,
            "stats": distribution_stats
        }
    
    def record_user_view(self, user_id: str, notice_id: str) -> bool:
        """Record that a user viewed a notice"""
        try:
            self.engagement_tracker.record_view(user_id, notice_id)
            if notice_id in self.notices:
                self.notices[notice_id].view_count += 1
            return True
        except Exception as e:
            print(f"Error recording view: {e}")
            return False
    
    def record_user_click(self, user_id: str, notice_id: str) -> bool:
        """Record that a user clicked on a notice"""
        try:
            self.engagement_tracker.record_click(user_id, notice_id)
            return True
        except Exception as e:
            print(f"Error recording click: {e}")
            return False
    
    def get_system_statistics(self) -> Dict:
        """Get overall system statistics"""
        return {
            "total_users": len(self.users),
            "total_notices": len(self.notices),
            "notifications_sent": self.notification_engine.notifications_sent,
            "notifications_failed": self.notification_engine.notifications_failed,
            "delivery_success_rate": self.notification_engine.get_delivery_success_rate(),
            "average_delivery_time_ms": self.notification_engine.get_average_delivery_time() * 1000
        }
    
    def get_notice_analytics(self, notice_id: str) -> Dict:
        """Get analytics for a specific notice"""
        if notice_id not in self.notices:
            return {}
            
        notice = self.notices[notice_id]
        engagement_rate = self.engagement_tracker.get_engagement_rate(notice_id)
        
        return {
            "notice_id": notice_id,
            "title": notice.title,
            "category": notice.category.value,
            "priority": notice.priority.value,
            "view_count": notice.view_count,
            "engagement_rate": engagement_rate,
            "created_at": notice.created_at.isoformat(),
            "expiry_date": notice.expiry_date.isoformat()
        }


# Example usage and testing
if __name__ == "__main__":
    import tempfile
    
    # Create system with temporary database
    db_file = tempfile.NamedTemporaryFile(suffix='.db', delete=False).name
    system = NoticeBoardSystem(db_path=db_file)
    
    # Create sample users
    user1 = User("U001", "Alice Johnson", "alice@college.edu", UserRole.STUDENT, "Computer Science", 2)
    user2 = User("U002", "Bob Smith", "bob@college.edu", UserRole.STUDENT, "Electronics", 1)
    user3 = User("U003", "Dr. Carol White", "carol@college.edu", UserRole.FACULTY, "Computer Science")
    user4 = User("U004", "Admin Dave", "dave@college.edu", UserRole.ADMIN, "Administration")
    
    system.add_user(user1)
    system.add_user(user2)
    system.add_user(user3)
    system.add_user(user4)
    
    # Create sample notices
    notice1 = Notice("N001", "Mid-Semester Examination Schedule", 
                    "The mid-semester examinations will be held from March 15-25, 2024.",
                    NoticeCategory.EXAMINATIONS, NoticePriority.HIGH, "U004")
    notice1.target_departments = ["Computer Science", "Electronics"]
    notice1.target_academic_years = [1, 2, 3, 4]
    
    notice2 = Notice("N002", "Scholarship Application Deadline", 
                    "Apply for merit-based scholarships by March 31, 2024.",
                    NoticeCategory.SCHOLARSHIPS, NoticePriority.MEDIUM, "U004")
    notice2.target_roles = ["student"]
    
    notice3 = Notice("N003", "Campus Placement Drive", 
                    "Leading tech companies will conduct recruitment on April 5, 2024.",
                    NoticeCategory.PLACEMENTS, NoticePriority.HIGH, "U004")
    notice3.target_academic_years = [3, 4]
    
    system.publish_notice(notice1)
    system.publish_notice(notice2)
    system.publish_notice(notice3)
    
    # Distribute notices
    print("Distributing notices...")
    result1 = system.distribute_notice("N001")
    print(f"Notice 1 Distribution: {result1['stats']}")
    
    result2 = system.distribute_notice("N002")
    print(f"Notice 2 Distribution: {result2['stats']}")
    
    result3 = system.distribute_notice("N003")
    print(f"Notice 3 Distribution: {result3['stats']}")
    
    # Record engagement
    system.record_user_view("U001", "N001")
    system.record_user_view("U001", "N001")
    system.record_user_click("U001", "N001")
    system.record_user_view("U002", "N001")
    
    # Get statistics
    print("\nSystem Statistics:")
    stats = system.get_system_statistics()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    # Get notice analytics
    print("\nNotice Analytics:")
    analytics = system.get_notice_analytics("N001")
    for key, value in analytics.items():
        print(f"  {key}: {value}")
