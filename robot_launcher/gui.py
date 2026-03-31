#!/usr/bin/env python3
"""
Robot Teleoperation Launch GUI
Controls remote server and local teleop clients with full argument configuration.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import subprocess
import json
import os
import threading
import signal
from pathlib import Path

class RobotLauncherGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🤖 Robot Teleoperation Launcher")
        self.root.geometry("900x750")
        
        # Configuration
        self.config_file = Path.home() / "robot_launcher_config.json"
        self.work_dir_image = Path.home() / "Projects/xr_teleoperate/teleop/teleimager"
        self.work_dir_teleop = Path.home() / "Projects/xr_teleoperate/teleop"
        self.processes = []
        
        # Default values (as requested)
        self.defaults = {
            'frequency': 30.0,
            'input_mode': 'controller',
            'display_mode': 'immersive',
            'arm': 'G1_29',
            'ee': 'dex3',
            'img_server_ip': '192.168.123.164',
            'network_interface': 'wlo1',
            'motion': True,
            'headless': False,
            'sim': False,
            'ipc': False,
            'affinity': False,
            'record': True,
            'task_dir': './utils/data/',
            'task_name': 'pick cube',
            'task_goal': 'pick up cube.',
            'task_desc': 'task description',
            'task_steps': 'step1: do this; step2: do that;',
            # PC2 Settings
            'pc2_user': 'unitree',
            'pc2_ip': '192.168.123.164',
            'pc2_pass': '',
            'sudo_pass': '',
            'conda_env_remote': 'teleimager',
            'conda_env_local': 'tv'
        }
        
        # Load saved config
        self.config = self.load_config()
        
        # Create UI
        self.create_widgets()
        
    def load_config(self):
        """Load configuration from file or use defaults"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    saved = json.load(f)
                    self.defaults.update(saved)
            except:
                pass
        return self.defaults
        
    def save_config(self):
        """Save current configuration to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            messagebox.showerror("Error", f"Could not save config: {e}")
    
    def create_widgets(self):
        """Create all GUI widgets"""
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Tab 1: Teleop Arguments
        self.teleop_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.teleop_frame, text="🎮 Teleop Arguments")
        self.create_teleop_tab()
        
        # Tab 2: Recording Settings
        self.record_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.record_frame, text="📹 Recording")
        self.create_record_tab()
        
        # Tab 3: Network & Server
        self.network_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.network_frame, text="🌐 Network & Server")
        self.create_network_tab()
        
        # Tab 4: Control Panel
        self.control_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.control_frame, text="🚀 Control Panel")
        self.create_control_tab()
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        self.status_bar = ttk.Label(self.root, textvariable=self.status_var, 
                                    relief='sunken', anchor='w')
        self.status_bar.pack(fill='x', side='bottom')
        
    def create_teleop_tab(self):
        """Create teleop arguments tab"""
        main_frame = ttk.Frame(self.teleop_frame)
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Left column
        left_frame = ttk.Frame(main_frame)
        left_frame.pack(side='left', fill='both', expand=True)
        
        # Frequency
        ttk.Label(left_frame, text="Frequency (Hz):").grid(row=0, column=0, sticky='w', pady=5)
        self.freq_var = tk.DoubleVar(value=self.config['frequency'])
        ttk.Spinbox(left_frame, from_=1, to=100, increment=1, 
                   textvariable=self.freq_var, width=10).grid(row=0, column=1, pady=5)
        
        # Input Mode
        ttk.Label(left_frame, text="Input Mode:").grid(row=1, column=0, sticky='w', pady=5)
        self.input_mode_var = tk.StringVar(value=self.config['input_mode'])
        input_combo = ttk.Combobox(left_frame, textvariable=self.input_mode_var, 
                                   values=['hand', 'controller'], width=27, state='readonly')
        input_combo.grid(row=1, column=1, pady=5)
        
        # Display Mode
        ttk.Label(left_frame, text="Display Mode:").grid(row=2, column=0, sticky='w', pady=5)
        self.display_mode_var = tk.StringVar(value=self.config['display_mode'])
        display_combo = ttk.Combobox(left_frame, textvariable=self.display_mode_var,
                                     values=['immersive', 'ego', 'pass-through'], 
                                     width=27, state='readonly')
        display_combo.grid(row=2, column=1, pady=5)
        
        # Arm
        ttk.Label(left_frame, text="Arm:").grid(row=3, column=0, sticky='w', pady=5)
        self.arm_var = tk.StringVar(value=self.config['arm'])
        arm_combo = ttk.Combobox(left_frame, textvariable=self.arm_var,
                                 values=['G1_29', 'G1_23', 'H1_2', 'H1'], 
                                 width=27, state='readonly')
        arm_combo.grid(row=3, column=1, pady=5)
        
        # End Effector
        ttk.Label(left_frame, text="End Effector:").grid(row=4, column=0, sticky='w', pady=5)
        self.ee_var = tk.StringVar(value=self.config['ee'])
        ee_combo = ttk.Combobox(left_frame, textvariable=self.ee_var,
                                values=['dex1', 'dex3', 'inspire_ftp', 'inspire_dfx', 'brainco'], 
                                width=27, state='readonly')
        ee_combo.grid(row=4, column=1, pady=5)
        
        # Right column
        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side='right', fill='both', expand=True)
        
        # Mode Flags
        ttk.Label(right_frame, text="Mode Flags:").grid(row=0, column=0, sticky='w', pady=10)
        
        self.motion_var = tk.BooleanVar(value=self.config['motion'])
        ttk.Checkbutton(right_frame, text="Motion Control", 
                       variable=self.motion_var).grid(row=1, column=0, sticky='w', pady=2)
        
        self.headless_var = tk.BooleanVar(value=self.config['headless'])
        ttk.Checkbutton(right_frame, text="Headless (No Display)", 
                       variable=self.headless_var).grid(row=2, column=0, sticky='w', pady=2)
        
        self.sim_var = tk.BooleanVar(value=self.config['sim'])
        ttk.Checkbutton(right_frame, text="Isaac Simulation", 
                       variable=self.sim_var).grid(row=3, column=0, sticky='w', pady=2)
        
        self.ipc_var = tk.BooleanVar(value=self.config['ipc'])
        ttk.Checkbutton(right_frame, text="IPC Server", 
                       variable=self.ipc_var).grid(row=4, column=0, sticky='w', pady=2)
        
        self.affinity_var = tk.BooleanVar(value=self.config['affinity'])
        ttk.Checkbutton(right_frame, text="High Priority CPU Affinity", 
                        variable=self.affinity_var).grid(row=5, column=0, sticky='w', pady=2)
        
        # Reset button
        ttk.Button(right_frame, text="🔄 Reset to Defaults", 
                  command=self.reset_teleop_defaults).grid(row=6, column=0, pady=20)
                  
    def create_record_tab(self):
        """Create recording settings tab"""
        main_frame = ttk.Frame(self.record_frame)
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Record toggle
        self.record_var = tk.BooleanVar(value=self.config['record'])
        record_check = ttk.Checkbutton(main_frame, text="Enable Data Recording", variable=self.record_var)
        record_check.pack(anchor='w', pady=10)
        
        # Task Directory
        ttk.Label(main_frame, text="Task Directory:").pack(anchor='w', pady=(20, 5))
        self.task_dir_var = tk.StringVar(value=self.config['task_dir'])
        dir_frame = ttk.Frame(main_frame)
        dir_frame.pack(fill='x', pady=5)
        ttk.Entry(dir_frame, textvariable=self.task_dir_var, width=50).pack(side='left')
        ttk.Button(dir_frame, text="Browse", 
                  command=self.browse_task_dir).pack(side='left', padx=5)
        
        # Task Name
        ttk.Label(main_frame, text="Task Name:").pack(anchor='w', pady=(20, 5))
        self.task_name_var = tk.StringVar(value=self.config['task_name'])
        ttk.Entry(main_frame, textvariable=self.task_name_var, width=60).pack(anchor='w', pady=5)
        
        # Task Goal
        ttk.Label(main_frame, text="Task Goal:").pack(anchor='w', pady=(20, 5))
        self.task_goal_var = tk.StringVar(value=self.config['task_goal'])
        ttk.Entry(main_frame, textvariable=self.task_goal_var, width=60).pack(anchor='w', pady=5)
        
        # Task Description
        ttk.Label(main_frame, text="Task Description:").pack(anchor='w', pady=(20, 5))
        self.task_desc_var = tk.StringVar(value=self.config['task_desc'])
        ttk.Entry(main_frame, textvariable=self.task_desc_var, width=60).pack(anchor='w', pady=5)
        
        # Task Steps
        ttk.Label(main_frame, text="Task Steps:").pack(anchor='w', pady=(20, 5))
        self.task_steps_var = tk.StringVar(value=self.config['task_steps'])
        ttk.Entry(main_frame, textvariable=self.task_steps_var, width=60).pack(anchor='w', pady=5)
        
    def create_network_tab(self):
        """Create network and server settings tab"""
        main_frame = ttk.Frame(self.network_frame)
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Image Server IP
        ttk.Label(main_frame, text="Image Server IP:").grid(row=0, column=0, sticky='w', pady=10)
        self.img_ip_var = tk.StringVar(value=self.config['img_server_ip'])
        ttk.Entry(main_frame, textvariable=self.img_ip_var, width=30).grid(row=0, column=1, pady=10)
        
        # Network Interface
        ttk.Label(main_frame, text="Network Interface:").grid(row=1, column=0, sticky='w', pady=10)
        self.net_interface_var = tk.StringVar(value=self.config['network_interface'])
        ttk.Entry(main_frame, textvariable=self.net_interface_var, width=30).grid(row=1, column=1, pady=10)
        
        # PC2 Settings
        ttk.Separator(main_frame, orient='horizontal').grid(row=2, column=0, columnspan=2, 
                                                           sticky='ew', pady=20)
        
        ttk.Label(main_frame, text="PC2 (Remote Server) Settings:", 
                 font=('Arial', 12, 'bold')).grid(row=3, column=0, columnspan=2, sticky='w', pady=10)
        
        ttk.Label(main_frame, text="Username:").grid(row=4, column=0, sticky='w', pady=5)
        self.pc2_user_var = tk.StringVar(value=self.config['pc2_user'])
        ttk.Entry(main_frame, textvariable=self.pc2_user_var, width=30).grid(row=4, column=1, pady=5)
        
        ttk.Label(main_frame, text="IP Address:").grid(row=5, column=0, sticky='w', pady=5)
        self.pc2_ip_var = tk.StringVar(value=self.config['pc2_ip'])
        ttk.Entry(main_frame, textvariable=self.pc2_ip_var, width=30).grid(row=5, column=1, pady=5)
        
        ttk.Label(main_frame, text="Password:").grid(row=6, column=0, sticky='w', pady=5)
        self.pc2_pass_var = tk.StringVar(value=self.config['pc2_pass'])
        ttk.Entry(main_frame, textvariable=self.pc2_pass_var, width=30, show='*').grid(row=6, column=1, pady=5)
        
        ttk.Label(main_frame, text="Sudo Password:").grid(row=7, column=0, sticky='w', pady=5)
        self.sudo_pass_var = tk.StringVar(value=self.config['sudo_pass'])
        ttk.Entry(main_frame, textvariable=self.sudo_pass_var, width=30, show='*').grid(row=7, column=1, pady=5)
        
        # Conda Environments
        ttk.Separator(main_frame, orient='horizontal').grid(row=8, column=0, columnspan=2, 
                                                           sticky='ew', pady=20)
        
        ttk.Label(main_frame, text="Conda Environments:", 
                 font=('Arial', 12, 'bold')).grid(row=9, column=0, columnspan=2, sticky='w', pady=10)
        
        ttk.Label(main_frame, text="Remote (PC2):").grid(row=10, column=0, sticky='w', pady=5)
        self.conda_remote_var = tk.StringVar(value=self.config['conda_env_remote'])
        ttk.Entry(main_frame, textvariable=self.conda_remote_var, width=30).grid(row=10, column=1, pady=5)
        
        ttk.Label(main_frame, text="Local (PC1):").grid(row=11, column=0, sticky='w', pady=5)
        self.conda_local_var = tk.StringVar(value=self.config['conda_env_local'])
        ttk.Entry(main_frame, textvariable=self.conda_local_var, width=30).grid(row=11, column=1, pady=5)
        
    def create_control_tab(self):
        """Create control panel tab"""
        main_frame = ttk.Frame(self.control_frame)
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Status indicators
        status_frame = ttk.LabelFrame(main_frame, text="System Status")
        status_frame.pack(fill='x', pady=10)
        
        self.remote_status = tk.StringVar(value="● Remote Server: Not Started")
        ttk.Label(status_frame, textvariable=self.remote_status, 
                 font=('Arial', 11)).pack(anchor='w', pady=5)
        
        self.client_status = tk.StringVar(value="● Local Clients: Not Started")
        ttk.Label(status_frame, textvariable=self.client_status, 
                 font=('Arial', 11)).pack(anchor='w', pady=5)
        
        # Control buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill='x', pady=20)
        
        ttk.Button(button_frame, text="🚀 Start Remote Server", 
                  command=self.start_remote_server, width=25).pack(pady=10)
        
        ttk.Button(button_frame, text="🎮 Start Local Clients", 
                  command=self.start_local_clients, width=25).pack(pady=10)
        
        ttk.Button(button_frame, text="⏹️ Stop All Processes", 
                  command=self.stop_all_processes, width=25).pack(pady=10)
        
        # Log output
        log_frame = ttk.LabelFrame(main_frame, text="Output Log")
        log_frame.pack(fill='both', expand=True, pady=10)
        
        self.log_text = tk.Text(log_frame, height=15, width=80)
        self.log_text.pack(fill='both', expand=True)
        
        scrollbar = ttk.Scrollbar(self.log_text, command=self.log_text.yview)
        scrollbar.pack(side='right', fill='y')
        self.log_text.config(yscrollcommand=scrollbar.set)
        
        # Save config button
        ttk.Button(main_frame, text="💾 Save Configuration", 
                  command=self.save_all_config).pack(pady=10)
        
    def log(self, message):
        """Add message to log"""
        self.log_text.insert('end', f"{message}\n")
        self.log_text.see('end')
        self.root.update_idletasks()
        
    def reset_teleop_defaults(self):
        """Reset teleop arguments to defaults"""
        self.freq_var.set(self.defaults['frequency'])
        self.input_mode_var.set(self.defaults['input_mode'])
        self.display_mode_var.set(self.defaults['display_mode'])
        self.arm_var.set(self.defaults['arm'])
        self.ee_var.set(self.defaults['ee'])
        self.motion_var.set(self.defaults['motion'])
        self.headless_var.set(self.defaults['headless'])
        self.sim_var.set(self.defaults['sim'])
        self.ipc_var.set(self.defaults['ipc'])
        self.affinity_var.set(self.defaults['affinity'])
        self.log("✅ Teleop arguments reset to defaults")
        
    def browse_task_dir(self):
        """Browse for task directory"""
        directory = filedialog.askdirectory(initialdir=self.task_dir_var.get())
        if directory:
            self.task_dir_var.set(directory)
            
    def build_teleop_command(self):
        """Build teleop_hand_and_arm.py command from GUI values"""
        cmd = ["python", "teleop_hand_and_arm.py"]
        
        cmd.extend(["--frequency", str(self.freq_var.get())])
        cmd.extend(["--input-mode", self.input_mode_var.get()])
        cmd.extend(["--display-mode", self.display_mode_var.get()])
        cmd.extend(["--arm", self.arm_var.get()])
        cmd.extend(["--ee", self.ee_var.get()])
        cmd.extend(["--img-server-ip", self.img_ip_var.get()])
        
        if self.net_interface_var.get():
            cmd.extend(["--network-interface", self.net_interface_var.get()])
        
        if self.motion_var.get():
            cmd.append("--motion")
        if self.headless_var.get():
            cmd.append("--headless")
        if self.sim_var.get():
            cmd.append("--sim")
        if self.ipc_var.get():
            cmd.append("--ipc")
        if self.affinity_var.get():
            cmd.append("--affinity")
        if self.record_var.get():
            cmd.append("--record")
            cmd.extend(["--task-dir", self.task_dir_var.get()])
            cmd.extend(["--task-name", self.task_name_var.get()])
            cmd.extend(["--task-goal", self.task_goal_var.get()])
            cmd.extend(["--task-desc", self.task_desc_var.get()])
            cmd.extend(["--task-steps", self.task_steps_var.get()])
        
        return cmd
        
    def start_remote_server(self):
        """Start remote server on PC2"""
        self.log("🔌 Starting remote server...")
        
        user = self.pc2_user_var.get()
        ip = self.pc2_ip_var.get()
        password = self.pc2_pass_var.get()
        sudo_pass = self.sudo_pass_var.get()
        conda_env = self.conda_remote_var.get()
        
        if not password:
            messagebox.showwarning("Warning", "PC2 password is empty. SSH may fail.")
        
        # Build SSH command
        ssh_cmd = f"""sshpass -p "{password}" ssh -o StrictHostKeyChecking=no {user}@{ip} "
            echo '{sudo_pass}' | sudo -S ip link set wlan0 down;
            source ~/miniconda3/etc/profile.d/conda.sh;
            conda activate {conda_env};
            teleimager-server
        " """
        
        try:
            # Start in background thread
            def run_ssh():
                try:
                    process = subprocess.Popen(ssh_cmd, shell=True, 
                                             stdout=subprocess.PIPE, 
                                             stderr=subprocess.PIPE,
                                             preexec_fn=os.setsid)
                    self.processes.append(process)
                    self.remote_status.set("● Remote Server: Running")
                    self.log("✅ Remote server started successfully")
                    
                    # Monitor output
                    for line in process.stdout:
                        self.log(f"[PC2] {line.decode().strip()}")
                        
                except Exception as e:
                    self.log(f"❌ Error: {e}")
                    self.remote_status.set("● Remote Server: Failed")
            
            thread = threading.Thread(target=run_ssh, daemon=True)
            thread.start()
            
            self.status_var.set("Remote server starting...")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start remote server: {e}")
            self.log(f"❌ Error: {e}")
            
    def start_local_clients(self):
        """Start local clients (image_client + teleop)"""
        self.log("🎮 Starting local clients...")
        
        conda_env = self.conda_local_var.get()
        work_dir_image = str(self.work_dir_image)
        work_dir_teleop = str(self.work_dir_teleop)
        
        try:
            # Client 1: Image Client
            client1_cmd = f"""gnome-terminal --tab --title="Image Client" -- bash -c "
                source ~/miniconda3/etc/profile.d/conda.sh;
                conda activate {conda_env};
                cd {work_dir_image};
                python -m teleimager.image_client --host {self.img_ip_var.get()};
                exec bash
            " """
            
            # Client 2: Teleop
            teleop_cmd = " ".join(self.build_teleop_command())
            client2_cmd = f"""gnome-terminal --tab --title="Teleop Control" -- bash -c "
                source ~/miniconda3/etc/profile.d/conda.sh;
                conda activate {conda_env};
                cd {work_dir_teleop};
                {teleop_cmd};
                exec bash
            " """
            
            # Execute commands
            subprocess.Popen(client1_cmd, shell=True)
            self.log("✅ Image client started")
            
            import time
            time.sleep(2)
            
            subprocess.Popen(client2_cmd, shell=True)
            self.log("✅ Teleop control started")
            
            self.client_status.set("● Local Clients: Running")
            self.status_var.set("Local clients started")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start local clients: {e}")
            self.log(f"❌ Error: {e}")
            
    def stop_all_processes(self):
        """Stop all running processes"""
        self.log("⏹️ Stopping all processes...")
        
        for process in self.processes:
            try:
                os.killpg(os.getpgid(process.pid), signal.SIGTERM)
                self.log(f"Stopped process {process.pid}")
            except:
                pass
        
        self.processes.clear()
        self.remote_status.set("● Remote Server: Stopped")
        self.client_status.set("● Local Clients: Stopped")
        self.status_var.set("All processes stopped")
        self.log("✅ All processes stopped")
        
    def save_all_config(self):
        """Save all configuration to file"""
        self.config.update({
            'frequency': self.freq_var.get(),
            'input_mode': self.input_mode_var.get(),
            'display_mode': self.display_mode_var.get(),
            'arm': self.arm_var.get(),
            'ee': self.ee_var.get(),
            'img_server_ip': self.img_ip_var.get(),
            'network_interface': self.net_interface_var.get(),
            'motion': self.motion_var.get(),
            'headless': self.headless_var.get(),
            'sim': self.sim_var.get(),
            'ipc': self.ipc_var.get(),
            'affinity': self.affinity_var.get(),
            'record': self.record_var.get(),
            'task_dir': self.task_dir_var.get(),
            'task_name': self.task_name_var.get(),
            'task_goal': self.task_goal_var.get(),
            'task_desc': self.task_desc_var.get(),
            'task_steps': self.task_steps_var.get(),
            'pc2_user': self.pc2_user_var.get(),
            'pc2_ip': self.pc2_ip_var.get(),
            'pc2_pass': self.pc2_pass_var.get(),
            'sudo_pass': self.sudo_pass_var.get(),
            'conda_env_remote': self.conda_remote_var.get(),
            'conda_env_local': self.conda_local_var.get()
        })
        
        self.save_config()
        messagebox.showinfo("Success", "Configuration saved successfully!")
        self.log("💾 Configuration saved")


def main():
    root = tk.Tk()
    app = RobotLauncherGUI(root)
    root.protocol("WM_DELETE_WINDOW", lambda: (app.stop_all_processes(), root.destroy()))
    root.mainloop()


if __name__ == "__main__":
    main()