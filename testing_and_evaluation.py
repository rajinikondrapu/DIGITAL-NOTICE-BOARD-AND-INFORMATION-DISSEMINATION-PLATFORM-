"""
Testing and Evaluation Module for Digital Notice Board System
Comprehensive performance testing and evaluation suite
"""

import tempfile
import time
import random
from datetime import datetime
import json
from typing import Dict
from notice_board_system import (
    NoticeBoardSystem, User, Notice, UserRole, 
    NoticeCategory, NoticePriority
)


class PerformanceTester:
    """Performance testing suite for the notice board system"""
    
    def __init__(self):
        self.db_file = tempfile.NamedTemporaryFile(suffix='.db', delete=False).name
        self.system = NoticeBoardSystem(db_path=self.db_file)
        self.test_results = {}
        
    def setup_test_data(self, num_users: int = 100, num_notices: int = 50) -> None:
        """Setup test data"""
        print(f"Setting up test data: {num_users} users, {num_notices} notices...")
        
        # Create users
        departments = ["Computer Science", "Electronics", "Mechanical", "Civil", "Chemical"]
        roles = [UserRole.STUDENT, UserRole.STUDENT, UserRole.STUDENT, UserRole.FACULTY, UserRole.ADMIN]
        
        for i in range(num_users):
            user_id = f"U{i:04d}"
            name = f"User {i}"
            email = f"user{i}@college.edu"
            role = random.choice(roles)
            department = random.choice(departments)
            academic_year = random.randint(1, 4) if role == UserRole.STUDENT else 1
            
            user = User(user_id, name, email, role, department, academic_year)
            self.system.add_user(user)
        
        # Create notices
        categories = list(NoticeCategory)
        priorities = list(NoticePriority)
        
        for i in range(num_notices):
            notice_id = f"N{i:04d}"
            title = f"Notice {i}: {random.choice(['Announcement', 'Update', 'Alert', 'Information'])}"
            content = f"This is the content for notice {i}. " * 5
            category = random.choice(categories)
            priority = random.choice(priorities)
            created_by = f"U{random.randint(0, num_users-1):04d}"
            
            notice = Notice(notice_id, title, content, category, priority, created_by)
            
            # Set targeting
            if random.random() > 0.3:
                notice.target_departments = random.sample(departments, random.randint(1, 3))
            if random.random() > 0.5:
                notice.target_academic_years = random.sample([1, 2, 3, 4], random.randint(1, 3))
            if random.random() > 0.6:
                notice.target_roles = random.sample([r.value for r in roles], random.randint(1, 3))
            
            self.system.publish_notice(notice)
    
    def test_notice_distribution_performance(self) -> Dict:
        """Test notice distribution performance"""
        print("\nTesting notice distribution performance...")
        
        results = {
            "test_name": "Notice Distribution Performance",
            "num_notices": len(self.system.notices),
            "num_users": len(self.system.users),
            "distribution_times": [],
            "total_notifications": 0,
            "failed_notifications": 0
        }
        
        for notice_id, notice in list(self.system.notices.items())[:10]:
            start_time = time.time()
            result = self.system.distribute_notice(notice_id)
            elapsed_time = time.time() - start_time
            
            results["distribution_times"].append(elapsed_time)
            results["total_notifications"] += result["stats"]["notified_users"]
            results["failed_notifications"] += result["stats"]["failed_deliveries"]
        
        results["average_distribution_time"] = sum(results["distribution_times"]) / len(results["distribution_times"])
        results["min_distribution_time"] = min(results["distribution_times"])
        results["max_distribution_time"] = max(results["distribution_times"])
        
        print(f"  Average distribution time: {results['average_distribution_time']*1000:.2f} ms")
        print(f"  Total notifications sent: {results['total_notifications']}")
        print(f"  Failed notifications: {results['failed_notifications']}")
        
        return results
    
    def test_notification_delivery_performance(self) -> Dict:
        """Test notification delivery performance"""
        print("\nTesting notification delivery performance...")
        
        results = {
            "test_name": "Notification Delivery Performance",
            "notifications_sent": 0,
            "delivery_times": [],
            "success_rate": 0.0,
            "average_delivery_time_ms": 0.0
        }
        
        # Distribute all notices
        for notice_id in list(self.system.notices.keys())[:5]:
            self.system.distribute_notice(notice_id)
        
        results["notifications_sent"] = self.system.notification_engine.notifications_sent
        results["success_rate"] = self.system.notification_engine.get_delivery_success_rate()
        results["average_delivery_time_ms"] = self.system.notification_engine.get_average_delivery_time() * 1000
        
        print(f"  Notifications sent: {results['notifications_sent']}")
        print(f"  Success rate: {results['success_rate']:.2f}%")
        print(f"  Average delivery time: {results['average_delivery_time_ms']:.2f} ms")
        
        return results
    
    def test_engagement_tracking_performance(self) -> Dict:
        """Test engagement tracking performance"""
        print("\nTesting engagement tracking performance...")
        
        results = {
            "test_name": "Engagement Tracking Performance",
            "total_views": 0,
            "total_clicks": 0,
            "average_engagement_rate": 0.0,
            "tracking_times": []
        }
        
        # Simulate user engagement
        num_interactions = 500
        for _ in range(num_interactions):
            user_id = random.choice(list(self.system.users.keys()))
            notice_id = random.choice(list(self.system.notices.keys()))
            
            start_time = time.time()
            self.system.record_user_view(user_id, notice_id)
            elapsed = time.time() - start_time
            results["tracking_times"].append(elapsed)
            
            if random.random() > 0.7:
                self.system.record_user_click(user_id, notice_id)
        
        results["total_views"] = sum(self.system.engagement_tracker.view_counts.values())
        results["total_clicks"] = sum(self.system.engagement_tracker.click_counts.values())
        
        if results["total_views"] > 0:
            results["average_engagement_rate"] = (results["total_clicks"] / results["total_views"]) * 100
        
        results["average_tracking_time_ms"] = (sum(results["tracking_times"]) / len(results["tracking_times"])) * 1000
        
        print(f"  Total views recorded: {results['total_views']}")
        print(f"  Total clicks recorded: {results['total_clicks']}")
        print(f"  Average engagement rate: {results['average_engagement_rate']:.2f}%")
        print(f"  Average tracking time: {results['average_tracking_time_ms']:.4f} ms")
        
        return results
    
    def test_personalization_performance(self) -> Dict:
        """Test personalization engine performance"""
        print("\nTesting personalization performance...")
        
        results = {
            "test_name": "Personalization Performance",
            "total_evaluations": 0,
            "evaluation_times": [],
            "average_evaluation_time_ms": 0.0
        }
        
        # Test personalization for all user-notice combinations
        test_count = min(100, len(self.system.users) * len(self.system.notices))
        
        for _ in range(test_count):
            user = random.choice(list(self.system.users.values()))
            notice = random.choice(list(self.system.notices.values()))
            
            start_time = time.time()
            should_notify = self.system.personalization_engine.should_notify_user(user, notice)
            relevance_score = self.system.personalization_engine.calculate_relevance_score(user, notice)
            elapsed = time.time() - start_time
            
            results["evaluation_times"].append(elapsed)
            results["total_evaluations"] += 1
        
        results["average_evaluation_time_ms"] = (sum(results["evaluation_times"]) / len(results["evaluation_times"])) * 1000
        
        print(f"  Total evaluations: {results['total_evaluations']}")
        print(f"  Average evaluation time: {results['average_evaluation_time_ms']:.4f} ms")
        
        return results
    
    def test_database_performance(self) -> Dict:
        """Test database performance"""
        print("\nTesting database performance...")
        
        results = {
            "test_name": "Database Performance",
            "insert_times": [],
            "query_times": [],
            "average_insert_time_ms": 0.0,
            "average_query_time_ms": 0.0
        }
        
        # Test inserts
        for i in range(50):
            user = User(f"PERF_U{i}", f"Perf User {i}", f"perfuser{i}@test.edu", 
                       UserRole.STUDENT, "Test Dept", 1)
            start_time = time.time()
            self.system.add_user(user)
            elapsed = time.time() - start_time
            results["insert_times"].append(elapsed)
        
        # Test queries
        for _ in range(50):
            user_id = random.choice(list(self.system.users.keys()))
            start_time = time.time()
            _ = self.system.users.get(user_id)
            elapsed = time.time() - start_time
            results["query_times"].append(elapsed)
        
        results["average_insert_time_ms"] = (sum(results["insert_times"]) / len(results["insert_times"])) * 1000
        results["average_query_time_ms"] = (sum(results["query_times"]) / len(results["query_times"])) * 1000
        
        print(f"  Average insert time: {results['average_insert_time_ms']:.4f} ms")
        print(f"  Average query time: {results['average_query_time_ms']:.4f} ms")
        
        return results
    
    def test_scalability(self) -> Dict:
        """Test system scalability"""
        print("\nTesting system scalability...")
        
        results = {
            "test_name": "Scalability Test",
            "user_counts": [10, 50, 100, 200],
            "distribution_times": [],
            "notifications_per_second": []
        }
        
        for user_count in results["user_counts"]:
            # Reset system
            self.system = NoticeBoardSystem(db_path=tempfile.NamedTemporaryFile(suffix='.db', delete=False).name)
            self.setup_test_data(num_users=user_count, num_notices=10)
            
            # Test distribution
            start_time = time.time()
            for notice_id in list(self.system.notices.keys())[:3]:
                self.system.distribute_notice(notice_id)
            elapsed = time.time() - start_time
            
            results["distribution_times"].append(elapsed)
            
            # Calculate notifications per second
            total_notified = self.system.notification_engine.notifications_sent
            nps = total_notified / elapsed if elapsed > 0 else 0
            results["notifications_per_second"].append(nps)
            
            print(f"  Users: {user_count}, Distribution time: {elapsed:.2f}s, Notifications/sec: {nps:.0f}")
        
        return results
    
    def run_all_tests(self) -> Dict:
        """Run all tests"""
        print("=" * 60)
        print("Digital Notice Board System - Performance Test Suite")
        print("=" * 60)
        
        self.setup_test_data(num_users=100, num_notices=50)
        
        all_results = {
            "test_timestamp": datetime.now().isoformat(),
            "tests": {}
        }
        
        all_results["tests"]["distribution"] = self.test_notice_distribution_performance()
        all_results["tests"]["delivery"] = self.test_notification_delivery_performance()
        all_results["tests"]["engagement"] = self.test_engagement_tracking_performance()
        all_results["tests"]["personalization"] = self.test_personalization_performance()
        all_results["tests"]["database"] = self.test_database_performance()
        all_results["tests"]["scalability"] = self.test_scalability()
        
        print("\n" + "=" * 60)
        print("Test Summary")
        print("=" * 60)
        
        system_stats = self.system.get_system_statistics()
        print(f"Total Users: {system_stats['total_users']}")
        print(f"Total Notices: {system_stats['total_notices']}")
        print(f"Notifications Sent: {system_stats['notifications_sent']}")
        print(f"Delivery Success Rate: {system_stats['delivery_success_rate']:.2f}%")
        print(f"Average Delivery Time: {system_stats['average_delivery_time_ms']:.2f} ms")
        
        return all_results


def main():
    """Main test execution"""
    tester = PerformanceTester()
    results = tester.run_all_tests()
    
    # Save results to file
    with open('/home/ubuntu/notice_report_project/test_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print("\nTest results saved to test_results.json")


if __name__ == "__main__":
    main()
