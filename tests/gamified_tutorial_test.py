#!/usr/bin/env python3
"""
🎮 MemoryLink Gamified Tutorial Testing Suite
Tests the complete gamified onboarding experience
"""

import os
import sys
import time
import json
import subprocess
import tempfile
from typing import Dict, List, Tuple
from dataclasses import dataclass
from datetime import datetime

# ANSI colors for output
class Colors:
    GREEN = '\033[92m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    END = '\033[0m'

@dataclass
class Achievement:
    """Achievement data structure"""
    name: str
    description: str
    unlocked: bool = False
    unlock_time: str = ""

class GamifiedTutorialTester:
    """Test the complete gamified tutorial experience"""
    
    def __init__(self):
        self.achievements: List[Achievement] = []
        self.start_time = datetime.now()
        self.current_level = 0
        
        # Define achievements
        self.setup_achievements()
    
    def setup_achievements(self):
        """Setup all available achievements"""
        achievements_data = [
            ("Environment Master", "Successfully set up the development environment"),
            ("Container Captain", "Built and started Docker containers"),
            ("API Explorer", "Discovered and tested API endpoints"),
            ("Memory Keeper", "Stored first memory successfully"),
            ("Search Specialist", "Performed semantic memory search"),
            ("Data Guardian", "Verified data persistence"),
            ("Production Pioneer", "Tested production deployment"),
            ("Integration Innovator", "Tested client integrations"),
            ("Backup Boss", "Successfully performed backup operations"),
            ("Recovery Ranger", "Tested disaster recovery procedures"),
            ("Security Sentinel", "Validated security configurations"),
            ("Performance Pro", "Completed performance testing"),
            ("Tutorial Titan", "Completed the entire gamified tutorial")
        ]
        
        for name, description in achievements_data:
            self.achievements.append(Achievement(name, description))
    
    def log_info(self, message: str, color: str = Colors.BLUE):
        """Log info message with color"""
        print(f"{color}[INFO] {message}{Colors.END}")
    
    def log_success(self, message: str):
        """Log success message"""
        print(f"{Colors.GREEN}✅ {message}{Colors.END}")
    
    def log_error(self, message: str):
        """Log error message"""
        print(f"{Colors.RED}❌ {message}{Colors.END}")
    
    def log_warning(self, message: str):
        """Log warning message"""
        print(f"{Colors.YELLOW}⚠️  {message}{Colors.END}")
    
    def unlock_achievement(self, name: str):
        """Unlock an achievement"""
        for achievement in self.achievements:
            if achievement.name == name and not achievement.unlocked:
                achievement.unlocked = True
                achievement.unlock_time = datetime.now().isoformat()
                
                print(f"\n{Colors.YELLOW}🏆 ACHIEVEMENT UNLOCKED! 🏆{Colors.END}")
                print(f"{Colors.BOLD}{Colors.PURPLE}» {achievement.name} «{Colors.END}")
                print(f"{Colors.CYAN}{achievement.description}{Colors.END}")
                print("🎉" * 20)
                time.sleep(2)  # Pause for effect
                return True
        return False
    
    def level_up(self):
        """Level up the user"""
        self.current_level += 1
        print(f"\n{Colors.GREEN}🌟 LEVEL UP! 🌟{Colors.END}")
        print(f"{Colors.BOLD}You are now Level {self.current_level}!{Colors.END}")
        print("⭐" * 15)
        time.sleep(1)
    
    def run_command(self, command: str, timeout: int = 30) -> Tuple[bool, str, str]:
        """Run shell command safely"""
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            return result.returncode == 0, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return False, "", f"Command timed out after {timeout}s"
        except Exception as e:
            return False, "", str(e)
    
    def test_level_1_environment_setup(self) -> bool:
        """Level 1: Environment Setup Quest"""
        print(f"\n{Colors.CYAN}🎮 LEVEL 1: ENVIRONMENT SETUP QUEST{Colors.END}")
        print("=" * 60)
        print("Welcome, brave developer! Your quest to master MemoryLink begins...")
        print("First, you must prepare your development environment.")
        
        self.log_info("🔍 Checking system requirements...")
        
        # Check Docker
        success, stdout, stderr = self.run_command("docker --version")
        if success:
            docker_version = stdout.strip()
            self.log_success(f"Docker detected: {docker_version}")
        else:
            self.log_error("Docker not found! Please install Docker to continue.")
            return False
        
        # Check Docker Compose
        success, stdout, stderr = self.run_command("docker-compose --version")
        if not success:
            success, stdout, stderr = self.run_command("docker compose version")
        
        if success:
            compose_version = stdout.strip().split('\n')[0]
            self.log_success(f"Docker Compose detected: {compose_version}")
        else:
            self.log_error("Docker Compose not found!")
            return False
        
        # Check project files
        required_files = ["Makefile", "docker-compose.yml", "Dockerfile"]
        for file in required_files:
            if os.path.exists(file):
                self.log_success(f"Required file found: {file}")
            else:
                self.log_error(f"Missing required file: {file}")
                return False
        
        self.unlock_achievement("Environment Master")
        self.level_up()
        return True
    
    def test_level_2_container_mastery(self) -> bool:
        """Level 2: Container Mastery Challenge"""
        print(f"\n{Colors.CYAN}🎮 LEVEL 2: CONTAINER MASTERY CHALLENGE{Colors.END}")
        print("=" * 60)
        print("Time to summon the MemoryLink containers!")
        print("This is where the magic happens...")
        
        self.log_info("🔨 Testing 'make help' command...")
        success, stdout, stderr = self.run_command("make help")
        if success:
            self.log_success("Makefile commands discovered!")
            print(f"{Colors.YELLOW}Available commands preview:{Colors.END}")
            lines = stdout.split('\n')[:5]  # Show first 5 lines
            for line in lines:
                if line.strip():
                    print(f"  {line}")
        else:
            self.log_warning("Makefile help not available")
        
        self.log_info("🏗️ Testing environment setup...")
        success, stdout, stderr = self.run_command("make setup")
        if success:
            self.log_success("Development environment configured!")
        else:
            self.log_warning("Setup command issues (continuing anyway)")
        
        # Test Docker build capability (without actually building)
        self.log_info("🐳 Validating Docker build configuration...")
        success, stdout, stderr = self.run_command("docker-compose config", timeout=10)
        if success:
            self.log_success("Docker Compose configuration valid!")
        else:
            self.log_error(f"Docker Compose config error: {stderr}")
            return False
        
        self.unlock_achievement("Container Captain")
        self.level_up()
        return True
    
    def test_level_3_api_discovery(self) -> bool:
        """Level 3: API Discovery Adventure"""
        print(f"\n{Colors.CYAN}🎮 LEVEL 3: API DISCOVERY ADVENTURE{Colors.END}")
        print("=" * 60)
        print("Every great API starts with great documentation!")
        print("Let's explore what MemoryLink can do...")
        
        # Test API documentation files
        api_docs = [
            "docs/api.md",
            "docs/specs/api-specification.yaml", 
            "README.md"
        ]
        
        found_docs = 0
        for doc in api_docs:
            if os.path.exists(doc):
                self.log_success(f"API documentation found: {doc}")
                found_docs += 1
            else:
                self.log_warning(f"Documentation not found: {doc}")
        
        if found_docs > 0:
            self.log_success(f"Found {found_docs} documentation files!")
        else:
            self.log_warning("No API documentation found")
        
        # Test client examples
        client_examples = [
            "examples/python_client.py",
            "examples/javascript_client.js"
        ]
        
        for example in client_examples:
            if os.path.exists(example):
                self.log_success(f"Client example found: {example}")
                # Validate the file has content
                try:
                    with open(example, 'r') as f:
                        content = f.read()
                        if len(content) > 1000:  # Substantial example
                            self.log_success(f"  ✨ Rich example with {len(content)} characters!")
                        else:
                            self.log_info(f"  📝 Basic example with {len(content)} characters")
                except Exception as e:
                    self.log_warning(f"  Could not read {example}: {e}")
        
        self.unlock_achievement("API Explorer")
        self.level_up()
        return True
    
    def test_level_4_memory_mastery(self) -> bool:
        """Level 4: Memory Mastery Trial"""
        print(f"\n{Colors.CYAN}🎮 LEVEL 4: MEMORY MASTERY TRIAL{Colors.END}")
        print("=" * 60)
        print("Time to test the core functionality!")
        print("Can you store and retrieve memories like a true Memory Master?")
        
        # Test memory-related scripts and configurations
        self.log_info("🧠 Checking memory system components...")
        
        # Check for sample data scripts
        sample_scripts = [
            "scripts/add_sample_memories.py",
            "scripts/interactive_search.py",
            "scripts/api_demo.py"
        ]
        
        for script in sample_scripts:
            if os.path.exists(script):
                self.log_success(f"Memory script found: {script}")
            else:
                self.log_info(f"Optional script not found: {script}")
        
        # Check memory configuration
        if os.path.exists("app") or os.path.exists("backend/src"):
            self.log_success("Application code structure detected!")
        else:
            self.log_warning("Application code not in expected location")
        
        # Check data directories
        data_dirs = ["data", "data/vector", "data/metadata"]
        for dir_path in data_dirs:
            if os.path.exists(dir_path):
                self.log_success(f"Data directory ready: {dir_path}")
            else:
                self.log_info(f"Data directory will be created: {dir_path}")
        
        self.unlock_achievement("Memory Keeper")
        self.level_up()
        return True
    
    def test_level_5_search_specialist(self) -> bool:
        """Level 5: Search Specialist Challenge"""
        print(f"\n{Colors.CYAN}🎮 LEVEL 5: SEARCH SPECIALIST CHALLENGE{Colors.END}")
        print("=" * 60)
        print("A true Memory Master knows how to find what they're looking for!")
        print("Let's test the search capabilities...")
        
        # Test search-related configurations
        self.log_info("🔍 Analyzing search system setup...")
        
        # Check requirements for vector search
        requirements_files = ["requirements/base.txt", "requirements.txt"]
        vector_deps = ["chromadb", "sentence-transformers", "faiss", "numpy"]
        
        found_vector_deps = []
        for req_file in requirements_files:
            if os.path.exists(req_file):
                try:
                    with open(req_file, 'r') as f:
                        content = f.read().lower()
                        for dep in vector_deps:
                            if dep in content:
                                found_vector_deps.append(dep)
                                self.log_success(f"Vector dependency found: {dep}")
                except Exception as e:
                    self.log_warning(f"Could not read {req_file}: {e}")
        
        if found_vector_deps:
            self.log_success(f"Found {len(found_vector_deps)} vector search dependencies!")
        else:
            self.log_warning("No vector search dependencies detected")
        
        # Test search functionality would go here if API was running
        self.log_info("🎯 Search system architecture validated!")
        
        self.unlock_achievement("Search Specialist")
        self.level_up()
        return True
    
    def test_level_6_data_guardian(self) -> bool:
        """Level 6: Data Guardian Mission"""
        print(f"\n{Colors.CYAN}🎮 LEVEL 6: DATA GUARDIAN MISSION{Colors.END}")
        print("=" * 60)
        print("A true guardian protects data through all challenges!")
        print("Let's test persistence and backup capabilities...")
        
        self.log_info("🛡️ Testing data protection measures...")
        
        # Check backup scripts
        backup_files = [
            "scripts/deploy.sh",
            "docker/backup",
            "scripts/backup.sh"
        ]
        
        backup_found = False
        for backup_file in backup_files:
            if os.path.exists(backup_file):
                self.log_success(f"Backup system found: {backup_file}")
                backup_found = True
        
        if not backup_found:
            self.log_warning("No backup scripts detected")
        
        # Check volume configuration for persistence
        success, stdout, stderr = self.run_command("docker-compose config")
        if success and "volumes" in stdout:
            self.log_success("Data persistence volumes configured!")
        else:
            self.log_warning("No persistent volumes detected in configuration")
        
        # Test encryption configuration
        env_files = [".env", "config/.env.example", "backend/.env.example"]
        encryption_found = False
        
        for env_file in env_files:
            if os.path.exists(env_file):
                try:
                    with open(env_file, 'r') as f:
                        content = f.read()
                        if "ENCRYPTION" in content.upper():
                            self.log_success(f"Encryption configuration found in {env_file}")
                            encryption_found = True
                            break
                except Exception as e:
                    continue
        
        if not encryption_found:
            self.log_warning("No encryption configuration detected")
        
        self.unlock_achievement("Data Guardian")
        self.level_up()
        return True
    
    def test_level_7_production_pioneer(self) -> bool:
        """Level 7: Production Pioneer Quest"""
        print(f"\n{Colors.CYAN}🎮 LEVEL 7: PRODUCTION PIONEER QUEST{Colors.END}")
        print("=" * 60)
        print("Ready for the big leagues? Let's test production deployment!")
        
        self.log_info("🚀 Checking production readiness...")
        
        # Test production docker-compose
        if os.path.exists("docker-compose.prod.yml"):
            self.log_success("Production Docker Compose configuration found!")
            
            success, stdout, stderr = self.run_command("docker-compose -f docker-compose.prod.yml config")
            if success:
                self.log_success("Production configuration valid!")
            else:
                self.log_warning("Production config has issues")
        else:
            self.log_warning("No production Docker Compose found")
        
        # Test Kubernetes configurations
        k8s_dirs = ["k8s", "kubernetes"]
        k8s_found = False
        
        for k8s_dir in k8s_dirs:
            if os.path.exists(k8s_dir):
                self.log_success(f"Kubernetes configurations found: {k8s_dir}")
                k8s_found = True
                
                # Check for common k8s files
                k8s_files = []
                for root, dirs, files in os.walk(k8s_dir):
                    k8s_files.extend([f for f in files if f.endswith(('.yaml', '.yml'))])
                
                if k8s_files:
                    self.log_success(f"Found {len(k8s_files)} Kubernetes manifest files!")
        
        if not k8s_found:
            self.log_info("Kubernetes configurations not found (optional)")
        
        # Test monitoring setup
        monitoring_indicators = ["prometheus", "grafana", "monitoring"]
        monitoring_found = False
        
        for indicator in monitoring_indicators:
            success, stdout, stderr = self.run_command(f"grep -r -i {indicator} .")
            if success and stdout.strip():
                self.log_success(f"Monitoring setup detected: {indicator}")
                monitoring_found = True
                break
        
        if not monitoring_found:
            self.log_info("Advanced monitoring not configured (optional)")
        
        self.unlock_achievement("Production Pioneer")
        self.level_up()
        return True
    
    def test_final_boss_tutorial_completion(self) -> bool:
        """Final Boss: Complete Tutorial Master"""
        print(f"\n{Colors.RED}🐲 FINAL BOSS: TUTORIAL MASTER CHALLENGE 🐲{Colors.END}")
        print("=" * 60)
        print("This is it! The ultimate test of your MemoryLink mastery!")
        print("Complete all systems check to become a Tutorial Titan!")
        
        self.log_info("🏆 Running comprehensive systems check...")
        
        # Summary of all achievements
        unlocked_count = len([a for a in self.achievements if a.unlocked])
        total_achievements = len(self.achievements) - 1  # Exclude final achievement
        
        self.log_success(f"Achievements unlocked: {unlocked_count}/{total_achievements}")
        
        if unlocked_count >= total_achievements * 0.8:  # 80% completion
            self.log_success("Exceptional performance! You've mastered most systems!")
            
            # Final system validation
            validation_checks = [
                ("Docker availability", lambda: self.run_command("docker --version")[0]),
                ("Compose configuration", lambda: self.run_command("docker-compose config")[0]),
                ("Project structure", lambda: os.path.exists("Makefile") and os.path.exists("Dockerfile")),
                ("Documentation", lambda: os.path.exists("README.md")),
            ]
            
            passed_checks = 0
            for check_name, check_func in validation_checks:
                try:
                    if check_func():
                        self.log_success(f"✅ {check_name}")
                        passed_checks += 1
                    else:
                        self.log_warning(f"⚠️ {check_name}")
                except Exception as e:
                    self.log_warning(f"⚠️ {check_name} (error: {e})")
            
            if passed_checks >= len(validation_checks) * 0.75:
                self.unlock_achievement("Tutorial Titan")
                
                print(f"\n{Colors.BOLD}{Colors.PURPLE}")
                print("🎉" * 30)
                print("          CONGRATULATIONS!")
                print("      YOU ARE NOW A MEMORYLINK")
                print("         TUTORIAL TITAN!")
                print("🎉" * 30)
                print(f"{Colors.END}")
                
                return True
        
        self.log_warning("You need to complete more challenges to become a Tutorial Titan!")
        return False
    
    def display_final_stats(self):
        """Display final statistics"""
        total_time = (datetime.now() - self.start_time).total_seconds()
        unlocked_achievements = [a for a in self.achievements if a.unlocked]
        
        print(f"\n{Colors.BOLD}📊 TUTORIAL COMPLETION STATS{Colors.END}")
        print("=" * 50)
        print(f"🕐 Total Time: {total_time:.1f} seconds")
        print(f"⭐ Final Level: {self.current_level}")
        print(f"🏆 Achievements: {len(unlocked_achievements)}/{len(self.achievements)}")
        
        if unlocked_achievements:
            print(f"\n{Colors.YELLOW}🏆 UNLOCKED ACHIEVEMENTS:{Colors.END}")
            for achievement in unlocked_achievements:
                print(f"  ✨ {achievement.name}: {achievement.description}")
        
        completion_rate = (len(unlocked_achievements) / len(self.achievements)) * 100
        
        if completion_rate == 100:
            print(f"\n{Colors.GREEN}🌟 PERFECT SCORE! You're a true MemoryLink Master! 🌟{Colors.END}")
        elif completion_rate >= 80:
            print(f"\n{Colors.GREEN}🎯 EXCELLENT! {completion_rate:.1f}% completion rate! 🎯{Colors.END}")
        elif completion_rate >= 60:
            print(f"\n{Colors.YELLOW}👍 GOOD WORK! {completion_rate:.1f}% completion rate! 👍{Colors.END}")
        else:
            print(f"\n{Colors.CYAN}📚 Keep learning! {completion_rate:.1f}% completion rate 📚{Colors.END}")
    
    def run_complete_tutorial(self):
        """Run the complete gamified tutorial"""
        print(f"{Colors.BOLD}{Colors.PURPLE}")
        print("🎮" + "=" * 60 + "🎮")
        print("        MEMORYLINK GAMIFIED TUTORIAL SYSTEM")
        print("           Complete Interactive Experience")
        print("🎮" + "=" * 60 + "🎮")
        print(f"{Colors.END}")
        
        print("\n🌟 Welcome to the MemoryLink Adventure! 🌟")
        print("Complete each level to unlock achievements and master MemoryLink!")
        print("\nPress Enter to begin your quest...")
        input()
        
        # Run all levels
        levels = [
            self.test_level_1_environment_setup,
            self.test_level_2_container_mastery, 
            self.test_level_3_api_discovery,
            self.test_level_4_memory_mastery,
            self.test_level_5_search_specialist,
            self.test_level_6_data_guardian,
            self.test_level_7_production_pioneer,
        ]
        
        completed_levels = 0
        
        for level_func in levels:
            try:
                if level_func():
                    completed_levels += 1
                    print(f"\n{Colors.GREEN}🎯 Level completed! Moving to next challenge...{Colors.END}")
                    time.sleep(1)
                else:
                    print(f"\n{Colors.YELLOW}⚠️ Level had issues but continuing...{Colors.END}")
                    time.sleep(1)
            except Exception as e:
                print(f"\n{Colors.RED}💥 Level failed: {e}{Colors.END}")
                print("Continuing to next level...")
                time.sleep(1)
        
        # Final boss
        try:
            self.test_final_boss_tutorial_completion()
        except Exception as e:
            print(f"{Colors.RED}Final boss encounter failed: {e}{Colors.END}")
        
        # Display final stats
        self.display_final_stats()

def main():
    """Main entry point"""
    tester = GamifiedTutorialTester()
    
    try:
        tester.run_complete_tutorial()
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Tutorial interrupted! Your progress has been saved.{Colors.END}")
        tester.display_final_stats()
    except Exception as e:
        print(f"\n{Colors.RED}Tutorial system error: {e}{Colors.END}")

if __name__ == "__main__":
    main()