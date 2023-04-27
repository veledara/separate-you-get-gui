from logging import config
from multiprocessing import Value
import tkinter as tk
from tkinter import ttk
import subprocess


class YouGetGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("you-get")
        self.root.geometry("450x100")
        self.root.resizable(False, False)

        self.dry_run_options_dict = {
            0: ("-i", "without urls"),
            1: ("-u", "with urls"),
            2: ("--json", "JSON format"),
        }
        self.download_options_checkboxes_dict = {
            0: (
                "--no-caption",
                "Do not download captions (subtitles, lyrics, danmaku)",
            ),
            1: ("--postfix", "Postfix downloaded files with unique identifiers"),
            2: ("-f", "Force overwriting existing files"),
            3: (
                "--skip-existing-file-size-check",
                "Skip existing file without checking file size",
            ),
            4: ("-c", "Load cookies.txt or cookies.sqlite"),
            5: ("-d", "Show traceback and other debug info"),
            6: ("-a", "Auto rename same name different files"),
            7: ("-k", "Ignore SSL errors"),
            8: ("-m", "Download video using an m3u8 URL"),
        }
        self.download_options_entries_dict = {
            0: ("-F", "Set video format to STREAM_ID:"),
            1: ("-O", "Set output filename:"),
            2: ("-o", "Set output directory:"),
            3: ("-p", "Stream extracted URL to a PLAYER:"),
            4: ("-t", "Set socket timeout:"),
        }
        self.proxy_options_dict = {
            0: ("-x", "HTTP proxy for downloading"),
            1: ("-y", "HTTP proxy for extracting only"),
            2: ("-s", "SOCKS5 proxy for downloading"),
        }
        self.other_options_dict = {
            0: ["", "Print extracted information"],
            1: ["--no-proxy", "Never use a proxy"],
        }

        self.url = ""
        self.selected_options = []
        self.availible_formats = ["mp4", "mp3"]

        self.first_step_widget()

    def first_step_widget(self):
        self.main_frame = ttk.Frame(self.root, padding="30 20")
        self.main_frame.grid(column=0, row=0, sticky=(tk.N, tk.W, tk.E, tk.S))

        self.url_text = tk.StringVar()
        self.url_text.set("Enter your URL here...")

        self.url_entry = ttk.Entry(
            self.main_frame, width=50, textvariable=self.url_text
        )
        self.url_entry.bind("<FocusIn>", self.clear_url_entry)
        self.url_entry.bind("<FocusOut>", self.restore_url_entry)
        self.url_entry.grid(column=0, row=0, padx=5, pady=5)

        self.continue_button = ttk.Button(
            self.main_frame, text="Continue", command=self.second_step_widget
        )
        self.continue_button.grid(column=1, row=0, padx=5, pady=5)

    def second_step_widget(self):
        self.url = self.url_entry.get()
        self.continue_button.grid_forget()
        self.url_entry.config(state="disabled")

        self.download_button = ttk.Button(
            self.main_frame, text="Download", command=self.download_video
        )

        self.download_button.grid(column=1, row=0, padx=5, pady=5)

        self.additional_frame = ttk.Frame(self.main_frame)
        self.additional_frame.grid(column=0, row=1, columnspan=2, sticky=tk.W)

        self.back_button = ttk.Button(
            self.additional_frame, text="Back", command=self.back_to_first_step
        )
        self.back_button.grid(column=0, row=0, padx=5, pady=5)

        self.format_combobox_text = tk.StringVar()
        self.format_combobox_text.set("Choose format...")
        self.format_combobox = ttk.Combobox(
            self.additional_frame,
            textvariable=self.format_combobox_text,
            state="readonly",
        )
        self.format_combobox["values"] = self.availible_formats

        self.format_combobox.grid(column=1, row=0, padx=5, pady=5)

        self.settings_button = ttk.Button(
            self.additional_frame, text="Settings", command=self.show_settings_window
        )
        self.settings_button.grid(column=2, row=0, padx=5, pady=5)

    def show_settings_window(self):
        # Создаем окно
        self.settings_window = tk.Toplevel(self.root)
        self.settings_window.title("Settings")
        self.settings_window.resizable(False, False)

        # Создаем переменные, в которых будут храниться настройки пользователя
        self.print_var = tk.BooleanVar()
        self.download_options_checkboxes_vars = [
            tk.BooleanVar() for _ in self.download_options_checkboxes_dict
        ]
        self.download_options_checkboxes_with_entry_vars = [
            tk.BooleanVar() for _ in self.download_options_entries_dict
        ]
        self.download_options_entries_vars = [
            tk.StringVar() for _ in self.download_options_entries_dict
        ]
        self.proxy_var = tk.BooleanVar()
        self.no_proxy_var = tk.BooleanVar()
        self.host_port_entry_var = tk.StringVar()

        # Запоминаем пользовательский выбор
        # remember the options ()
        # for i in self.selected_options:
        #     self.option_vars[i].set(True)

        # Создаем фреймы для каждого блока
        self.dry_run_labelframe = tk.LabelFrame(self.settings_window, text="Dry run")
        self.dry_run_labelframe.grid(
            column=0, row=0, sticky=(tk.N, tk.W, tk.E, tk.S), padx=20, pady=5
        )

        self.download_options_labelframe = tk.LabelFrame(
            self.settings_window, text="Download options"
        )
        self.download_options_labelframe.grid(
            column=0, row=1, sticky=(tk.N, tk.W, tk.E, tk.S), padx=20, pady=5
        )

        self.download_options_checkboxes_frame = tk.Frame(
            self.download_options_labelframe
        )
        self.download_options_checkboxes_frame.grid(
            column=0, row=0, sticky=(tk.N, tk.W, tk.E, tk.S)
        )
        self.download_options_entries_frame = tk.Frame(self.download_options_labelframe)
        self.download_options_entries_frame.grid(
            column=1, row=0, sticky=(tk.N, tk.W, tk.E, tk.S), padx=20
        )

        self.proxy_options_labelframe = tk.LabelFrame(
            self.settings_window, text="Proxy options"
        )
        self.proxy_options_labelframe.grid(
            column=0, row=2, sticky=(tk.N, tk.W, tk.E, tk.S), padx=20, pady=5
        )

        # Заполняем фреймы содержимым
        self.dry_run_handler()
        self.download_options_checkboxes_handler()
        self.download_options_entries_handler()
        self.proxy_options_handler()

        # Заполняем фрейм для кнопок и сами кнопки
        self.button_frame = tk.Frame(self.settings_window)
        self.button_frame.grid(column=0, row=3)

        cancel_button = ttk.Button(
            self.button_frame,
            text="Cancel",
            command=self.hide_settings_window,
            width=15,
        )
        cancel_button.grid(row=0, column=0, padx=10, pady=5, sticky="w")

        save_button = ttk.Button(
            self.button_frame,
            text="Save Settings",
            command=self.save_settings,
            width=15,
        )
        save_button.grid(row=0, column=1, padx=10, pady=5, sticky="e")

    def dry_run_handler(self):
        self.print_checkbox = ttk.Checkbutton(
            self.dry_run_labelframe,
            text="Print extracted information",
            variable=self.print_var,
            onvalue=True,
            offvalue=False,
            command=lambda: self.print_combobox.config(state="readonly")
            if self.print_var.get()
            else self.print_combobox.config(state="disabled"),
        )
        self.print_checkbox.grid(column=0, row=0, pady=5)

        self.print_combobox_text = tk.StringVar()
        self.print_combobox_text.set("without urls")
        self.print_combobox = ttk.Combobox(
            self.dry_run_labelframe,
            textvariable=self.print_combobox_text,
            state="disabled",
        )
        self.print_list = [value[1] for value in self.dry_run_options_dict.values()]
        self.print_combobox["values"] = list(self.print_list)
        self.print_combobox.grid(column=1, row=0, padx=5, pady=5)

    def download_options_checkboxes_handler(self):
        for key, value in self.download_options_checkboxes_dict.items():
            option_checkbox = ttk.Checkbutton(
                self.download_options_checkboxes_frame,
                text=value[1],
                variable=self.download_options_checkboxes_vars[key],
                onvalue=True,
                offvalue=False,
            )
            option_checkbox.pack(pady=2, anchor="w")

    def download_options_entries_handler(self):
        for key, value in self.download_options_entries_dict.items():
            option_checkbox_with_entry = ttk.Checkbutton(
                self.download_options_entries_frame,
                text=value[1],
                variable=self.download_options_checkboxes_with_entry_vars[key],
                onvalue=True,
                offvalue=False,
                command=lambda key=key: self.download_option_entry_handle(key),
            )
            option_checkbox_with_entry.grid(
                row=key, column=0, padx=10, pady=5, sticky="w"
            )
            option_entry_for_checkbox = ttk.Entry(
                self.download_options_entries_frame,
                width=15,
                textvariable=self.download_options_entries_vars[key],
                state="disabled",
            )
            option_entry_for_checkbox.grid(row=key, column=1, padx=10, pady=5)

    def proxy_options_handler(self):
        self.proxy_checkbox = ttk.Checkbutton(
            self.proxy_options_labelframe,
            text="Use",
            variable=self.proxy_var,
            onvalue=True,
            offvalue=False,
            command=lambda: self.proxy_options_enabled()
            if self.proxy_var.get()
            else self.proxy_options_disabled(),
        )
        self.proxy_checkbox.grid(column=0, row=0, pady=5, sticky="w")

        self.proxy_combobox_text = tk.StringVar()
        self.proxy_combobox_text.set("HTTP proxy for downloading")
        self.proxy_combobox = ttk.Combobox(
            self.proxy_options_labelframe,
            width="30",
            textvariable=self.proxy_combobox_text,
            state="disabled",
        )
        self.proxy_list = [value[1] for value in self.proxy_options_dict.values()]
        self.proxy_combobox["values"] = list(self.proxy_list)
        self.proxy_combobox.grid(column=1, row=0, pady=5)

        self.host_port_label = ttk.Label(
            self.proxy_options_labelframe, text="Enter HOST::PORT: ", state="disabled"
        )
        self.host_port_label.grid(column=2, row=0, padx=10, pady=5)

        self.host_port_entry = ttk.Entry(
            self.proxy_options_labelframe,
            width=15,
            textvariable=self.host_port_entry_var,
            state="disabled",
        )
        self.host_port_entry.grid(column=3, row=0, padx=5, pady=5)

        self.no_proxy_checkbox = ttk.Checkbutton(
            self.proxy_options_labelframe,
            text=self.other_options_dict.get(1)[1],
            variable=self.no_proxy_var,
            onvalue=True,
            offvalue=False,
            command=lambda: self.no_proxy_option_enabled()
            if self.no_proxy_var.get()
            else self.no_proxy_options_disabled(),
        )
        self.no_proxy_checkbox.grid(column=0, row=1, pady=5)

    # def download_options_enabled(self):
    #     for widget in (
    #         self.download_options_checkboxes_frame.winfo_children()
    #         + self.download_options_entries_frame.winfo_children()
    #     ):
    #         widget.config(state="normal")

    # def download_options_disabled(self):
    #     for i, widget in enumerate(
    #         self.download_options_checkboxes_frame.winfo_children()
    #     ):
    #         widget.config(state="disabled")
    #     entry_widgets = [
    #         widget
    #         for widget in self.download_options_entries_frame.winfo_children()
    #         if isinstance(widget, ttk.Entry)
    #     ]
    #     for i, widget in enumerate(entry_widgets):
    #         widget.config(state="disabled")
    def get_corresponding_entry(self, key):
        entries = [
            widget
            for widget in self.download_options_entries_frame.winfo_children()
            if isinstance(widget, ttk.Entry)
        ]
        return entries[key]

    def download_option_entry_handle(self, key):
        self.get_corresponding_entry(key).config(
            state="normal"
            if self.download_options_checkboxes_with_entry_vars[key].get()
            else "disabled"
        )

    def proxy_options_enabled(self):
        self.proxy_combobox.config(state="readonly")
        self.host_port_label.config(state="normal")
        self.host_port_entry.config(state="normal")

    def proxy_options_disabled(self):
        self.proxy_combobox.config(state="disabled")
        self.host_port_label.config(state="disabled")
        self.host_port_entry.config(state="disabled")

    def no_proxy_option_enabled(self):
        self.proxy_options_disabled()
        self.proxy_checkbox.config(state="disabled")
        self.proxy_var.set("False")

    def no_proxy_options_disabled(self):
        self.proxy_checkbox.config(state="normal")

    def hide_settings_window(self):
        self.settings_window.withdraw()

    def back_to_first_step(self):
        self.selected_options = []
        self.availible_formats = ["mp4", "mp3"]
        self.first_step_widget()

    def save_settings(self):
        self.selected_options.clear()

        self.selected_print_options: int
        self.selected_download_options = []
        self.selected_download_options_entries = {}
        self.selected_proxy_options = []

        if self.print_var.get():
            self.selected_print_options = self.print_combobox.current()

        for key, value in self.download_options_checkboxes_dict.items():
            if self.download_options_checkboxes_vars[key].get():
                self.selected_download_options.append(key)

        for key, value in self.download_options_entries_dict.items():
            if self.download_options_checkboxes_with_entry_vars[key].get():
                entry_text = self.get_corresponding_entry(key).get()
                self.selected_download_options_entries[key] = entry_text

        if self.proxy_var.get():
            self.selected_proxy_options.append(self.proxy_combobox.current())
            self.selected_proxy_options.append(self.host_port_entry.get())

        if self.no_proxy_var.get():
            self.selected_proxy_options.append("--no-proxy")

        print(self.selected_print_options)
        print(self.selected_download_options)
        print(self.selected_download_options_entries)
        print(self.selected_proxy_options)

        self.hide_settings_window()

    def download_video(self):
        cmd = ["you-get"]
        for key in self.selected_options:
            cmd += [self.download_options_checkboxes_dict.get(key)[0]]
        cmd += [self.url]
        print(cmd)

    def clear_url_entry(self, event):
        if self.url_entry.get() == "Enter your URL here...":
            self.url_entry.delete(0, tk.END)

    def restore_url_entry(self, event):
        if not self.url_entry.get():
            self.url_entry.insert(0, "Enter your URL here...")

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    YouGetGUI().run()
