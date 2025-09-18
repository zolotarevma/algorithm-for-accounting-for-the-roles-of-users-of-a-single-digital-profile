import tkinter as tk
from tkinter import messagebox
from datetime import datetime
from PIL import Image, ImageTk
import csv
from tkinter import ttk


def load_users_from_csv(filename="users.csv"):
    """Загружает пользователей из CSV файла"""
    users = {}
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                users[row['login']] = {
                    'password': row['password'],
                    'role': row['role'],
                    'full_name': row['full_name'],
                    'verified': row['verified'].lower() == 'true',
                    'categories': row['categories'].split(';') if row['categories'] else []
                }
    except FileNotFoundError:
        print(f"Файл {filename} не найден. Используются тестовые данные.")
    return users


def load_events_from_csv(filename="events.csv"):
    """Загружает мероприятия из CSV файла"""
    events = {}
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                current_participants = row.get('current_participants')
                scanned_count = row.get('scanned_count')

                events[int(row['id'])] = {
                    'title': row['title'],
                    'description': row['description'],
                    'start_date': row['start_date'],
                    'end_date': row['end_date'],
                    'location': row['location'],
                    'categories': row['categories'].split(';') if row['categories'] else [],
                    'organizer': row['organizer'],
                    'organizer_login': row['organizer_login'],
                    'current_participants': int(current_participants) if current_participants else 0,
                    'scanned_count': int(scanned_count) if scanned_count else 0
                }
    except FileNotFoundError:
        print(f"Файл {filename} не найден. Используются тестовые данные.")
    return events


def delete_event_from_csv(event_id, filename="events.csv"):
    """Удаляет мероприятие из CSV файла"""
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            rows = list(reader)

        rows = [row for row in rows if int(row['id']) != event_id]

        with open(filename, 'w', encoding='utf-8', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['id', 'title', 'description', 'start_date', 'end_date',
                             'location', 'categories', 'organizer', 'organizer_login',
                             'current_participants', 'scanned_count'])

            for row in rows:
                writer.writerow([
                    row['id'],
                    row['title'],
                    row['description'],
                    row['start_date'],
                    row['end_date'],
                    row['location'],
                    row['categories'],
                    row['organizer'],
                    row['organizer_login'],
                    row['current_participants'],
                    row['scanned_count']
                ])

        return True
    except Exception as e:
        print(f"Ошибка при удалении мероприятия: {e}")
        return False


def load_registrations_from_csv(filename="registrations.csv"):
    """Загружает регистрации из CSV файла"""
    registrations = {}
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                key = (row['user_login'], int(row['event_id']))
                registrations[key] = {
                    'status': row['status']
                }
    except FileNotFoundError:
        print(f"Файл {filename} не найден. Используются тестовые данные.")
    return registrations


def save_registrations_to_csv(registrations, filename="registrations.csv"):
    """Сохраняет регистрации в CSV файл"""
    try:
        with open(filename, 'w', encoding='utf-8', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['user_login', 'event_id', 'registration_date', 'status'])
            for (user_login, event_id), data in registrations.items():
                writer.writerow([user_login, event_id, data['status']])
    except Exception as e:
        print(f"Ошибка при сохранении регистраций: {e}")


users = load_users_from_csv()
events = load_events_from_csv()
registrations = load_registrations_from_csv()


class LoginWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Вход в систему")
        self.root.geometry("1000x700")
        #self.root.attributes('-fullscreen', True)

        # Поля для ввода
        tk.Label(self.root, text="Логин:").pack(pady=5)
        self.login_entry = tk.Entry(self.root)
        self.login_entry.insert(0, "organizer")
        self.login_entry.pack(pady=5)

        tk.Label(self.root, text="Пароль:").pack(pady=5)
        self.password_entry = tk.Entry(self.root, show="*")
        self.password_entry.insert(0, "1234")
        self.password_entry.pack(pady=5)

        # Кнопка входа
        self.login_button = tk.Button(self.root, text="Войти", command=self.check_credentials)
        self.login_button.pack(pady=10)

    def check_credentials(self):
        login = self.login_entry.get()
        password = self.password_entry.get()

        if login in users and users[login]["password"] == password:
            user_data = users[login].copy()
            user_data['login'] = login
            self.root.destroy()
            MainWindow(users[login]["role"], login, user_data)
        else:
            messagebox.showerror("Ошибка", "Неверный логин или пароль")

    def run(self):
        self.root.mainloop()


class ProfileWindow:
    def __init__(self, parent, login):
        self.parent = parent
        self.window = tk.Toplevel(parent)
        self.window.title("Мой профиль")
        self.window.geometry("1000x700")
        #self.window.attributes('-fullscreen', True)
        self.window.protocol("WM_DELETE_WINDOW", self.go_back)

        user_data = users[login]

        tk.Label(self.window, text=f"ФИО: {user_data['full_name']}",
                 font=("Arial", 12)).pack(pady=20)

        status_text = "Согласие подтверждено" if user_data['verified'] else "Отсутствует согласие"
        status_color = "green" if user_data['verified'] else "red"
        tk.Label(self.window, text=status_text,
                 fg=status_color, font=("Arial", 10)).pack(pady=10)

        if user_data['verified'] and user_data['role'] == 'user' and 'categories' in user_data:
            tk.Label(self.window, text="Категории:",
                     font=("Arial", 10, "bold")).pack(pady=(20, 5))

            for category in user_data['categories']:
                tk.Label(self.window, text=f"• {category}",
                         font=("Arial", 9)).pack()
            self.add_qr_code()

        tk.Button(self.window, text="Назад", command=self.go_back).pack(pady=20)

    def add_qr_code(self):
        qr_image = Image.open("user_qr_code.png")

        qr_image = qr_image.resize((200, 200), Image.Resampling.LANCZOS)

        photo = ImageTk.PhotoImage(qr_image)

        qr_frame = tk.Frame(self.window)
        qr_frame.pack(pady=20)

        qr_label = tk.Label(qr_frame, image=photo)
        qr_label.image = photo
        qr_label.pack()

        tk.Label(qr_frame, text="Ваш QR-код для использования на мероприятиях", font=("Arial", 9)).pack(pady=5)

    def go_back(self):
        self.window.destroy()
        self.parent.deiconify()


class EventsWindow:
    def __init__(self, parent, user_data):
        self.parent = parent
        self.user_data = user_data
        self.window = tk.Toplevel(parent)
        self.window.title("Мероприятия")
        self.window.geometry("1000x700")
        #self.window.attributes('-fullscreen', True)
        self.window.protocol("WM_DELETE_WINDOW", self.go_back)

        tk.Label(self.window, text="Доступные мероприятия",
                 font=("Arial", 16, "bold")).pack(pady=20)

        self.events_frame = tk.Frame(self.window)
        self.events_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        scrollbar = tk.Scrollbar(self.events_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.canvas = tk.Canvas(self.events_frame, yscrollcommand=scrollbar.set)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.canvas.yview)

        self.cards_frame = tk.Frame(self.canvas)
        self.canvas_window = self.canvas.create_window((0, 0), window=self.cards_frame, anchor="nw")

        tk.Button(self.window, text="Назад", command=self.go_back).pack(pady=10)

        self.display_events()

        self.cards_frame.bind("<Configure>", self.on_frame_configure)
        self.canvas.bind("<Configure>", self.on_canvas_configure)

    def display_events(self):
        for widget in self.cards_frame.winfo_children():
            widget.destroy()

        sorted_events = self.sort_events_by_priority(events)

        for event_id, event in sorted_events:
            self.create_event_card(event_id, event)

    def create_event_card(self, event_id, event):
        card = tk.Frame(self.cards_frame, relief=tk.RAISED, borderwidth=1, padx=10, pady=10)
        card.pack(fill=tk.X, pady=5, padx=5)

        tk.Label(card, text=event['title'], font=("Arial", 12, "bold")).pack(anchor="w")

        start_date = datetime.strptime(event['start_date'], "%Y-%m-%d %H:%M")
        end_date = datetime.strptime(event['end_date'], "%Y-%m-%d %H:%M")
        date_text = f"{start_date.strftime('%d.%m.%Y %H:%M')} - {end_date.strftime('%d.%m.%Y %H:%M')}"
        tk.Label(card, text=date_text, font=("Arial", 9)).pack(anchor="w")

        tk.Label(card, text=f"Место: {event['location']}", font=("Arial", 9)).pack(anchor="w")

        tk.Label(card, text=f"Организатор: {event['organizer']}", font=("Arial", 9)).pack(anchor="w")

        categories_text = f"Категории: {', '.join(event['categories'])}"
        tk.Label(card, text=categories_text, font=("Arial", 9)).pack(anchor="w")

        tk.Button(card, text="Подробнее",
                  command=lambda eid=event_id: self.show_event_details(eid)).pack(anchor="e", pady=5)

    def sort_events_by_priority(self, events_dict):
        """
        Сортирует мероприятия по приоритету:
        1. По количеству совпадений категорий (убывание)
        2. По дате начала (ближайшие сначала)
        """
        if not self.user_data.get('verified') or self.user_data.get(
                'role') != 'user' or 'categories' not in self.user_data:
            return sorted(events_dict.items(),
                          key=lambda x: datetime.strptime(x[1]['start_date'], "%Y-%m-%d %H:%M"))

        user_categories = self.user_data['categories']

        events_with_priority = []
        for event_id, event in events_dict.items():
            match_count = count_category_matches(event['categories'], user_categories)
            events_with_priority.append((event_id, event, match_count))

        events_with_priority.sort(key=lambda x: (-x[2], datetime.strptime(x[1]['start_date'], "%Y-%m-%d %H:%M")))

        return [(event_id, event) for event_id, event, _ in events_with_priority]

    def show_event_details(self, event_id):
        self.window.withdraw()
        EventDetailsWindow(self.window, event_id, events[event_id], self.user_data['login'])

    def on_frame_configure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def on_canvas_configure(self, event):
        self.canvas.itemconfig(self.canvas_window, width=event.width)

    def go_back(self):
        self.window.destroy()
        self.parent.deiconify()


class EventDetailsWindow:
    def __init__(self, parent, event_id, event_data, user_login):
        self.parent = parent
        self.event_id = event_id
        self.event_data = event_data
        self.user_login = user_login
        self.window = tk.Toplevel(parent)
        self.window.title(f"Мероприятие: {event_data['title']}")
        self.window.geometry("1000x700")
        #self.window.attributes('-fullscreen', True)
        self.window.protocol("WM_DELETE_WINDOW", self.go_back)

        tk.Label(self.window, text=event_data['title'],
                 font=("Arial", 16, "bold")).pack(pady=20)

        info_frame = tk.Frame(self.window)
        info_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        start_date = datetime.strptime(event_data['start_date'], "%Y-%m-%d %H:%M")
        end_date = datetime.strptime(event_data['end_date'], "%Y-%m-%d %H:%M")
        date_text = f"Дата и время: {start_date.strftime('%d.%m.%Y %H:%M')} - {end_date.strftime('%d.%m.%Y %H:%M')}"
        tk.Label(info_frame, text=date_text, font=("Arial", 11)).pack(anchor="w", pady=5)

        tk.Label(info_frame, text=f"Место: {event_data['location']}",
                 font=("Arial", 11)).pack(anchor="w", pady=5)

        tk.Label(info_frame, text=f"Организатор: {event_data['organizer']}",
                 font=("Arial", 11)).pack(anchor="w", pady=5)

        categories_text = f"Категории: {', '.join(event_data['categories'])}"
        tk.Label(info_frame, text=categories_text,
                 font=("Arial", 11)).pack(anchor="w", pady=5)

        tk.Label(info_frame, text="Описание:",
                 font=("Arial", 11, "bold")).pack(anchor="w", pady=(20, 5))

        description_text = tk.Text(info_frame, wrap=tk.WORD, height=8,
                                   font=("Arial", 10), relief=tk.FLAT)
        description_text.insert(tk.END, event_data['description'])
        description_text.config(state=tk.DISABLED)
        description_text.pack(fill=tk.X, pady=5)

        is_registered = (user_login, event_id) in registrations

        user_data = users[user_login]
        if user_data['verified'] and user_data['role'] == 'user':
            if not is_registered:
                tk.Button(info_frame, text="Зарегистрироваться",
                            command=self.register_for_event).pack(pady=10)
            else:
                tk.Label(info_frame, text="Вы уже зарегистрированы на это мероприятие",
                            fg="green", font=("Arial", 11)).pack(pady=10)
                tk.Button(info_frame, text="Отменить регистрацию",
                            command=self.cancel_registration).pack(pady=5)
        else:
            if not user_data['verified']:
                tk.Label(info_frame, text="Для регистрации подтвердите согласие",
                         fg="red", font=("Arial", 11)).pack(pady=10)

        tk.Button(self.window, text="Назад", command=self.go_back).pack(pady=10)

    def register_for_event(self):
        registrations[(self.user_login, self.event_id)] = {
            'status': 'registered'
        }

        save_registrations_to_csv(registrations)

        messagebox.showinfo("Успех", "Вы успешно зарегистрировались на мероприятие!")

        self.window.destroy()
        EventDetailsWindow(self.parent, self.event_id, events[self.event_id], self.user_login)

    def cancel_registration(self):
        if (self.user_login, self.event_id) in registrations:
            del registrations[(self.user_login, self.event_id)]

            save_registrations_to_csv(registrations)

            messagebox.showinfo("Успех", "Регистрация на мероприятие отменена!")

            self.window.destroy()
            EventDetailsWindow(self.parent, self.event_id, events[self.event_id], self.user_login)

    def go_back(self):
        self.window.destroy()
        self.parent.deiconify()


class OrganizerWindow:
    def __init__(self, parent, user_data):
        self.parent = parent
        self.user_data = user_data
        self.window = tk.Toplevel(parent)
        self.window.title("Панель организатора")
        self.window.geometry("1000x700")
        self.window.protocol("WM_DELETE_WINDOW", self.go_back)

        tk.Label(self.window, text="Панель организатора мероприятий",
                 font=("Arial", 16, "bold")).pack(pady=20)

        button_frame = tk.Frame(self.window)
        button_frame.pack(pady=10)

        tk.Button(button_frame, text="Мои мероприятия", width=20,
                  command=self.show_my_events).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Создать мероприятие", width=20,
                  command=self.create_event).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Статистика", width=20,
                  command=self.show_statistics).pack(side=tk.LEFT, padx=5)

        self.content_frame = tk.Frame(self.window)
        self.content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # Кнопка назад
        tk.Button(self.window, text="Назад", command=self.go_back).pack(pady=10)

        self.show_my_events()

    def show_my_events(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        tk.Label(self.content_frame, text="Мои мероприятия",
                 font=("Arial", 14)).pack(pady=10)

        my_events = {id: event for id, event in events.items()
                     if event.get('organizer_login') == self.user_data['login']}

        if not my_events:
            tk.Label(self.content_frame, text="У вас пока нет мероприятий").pack(pady=20)
            return

        columns = ("Название", "Дата", "Место", "Зарегистрировано", "Посещения")
        tree = ttk.Treeview(self.content_frame, columns=columns, show="headings", height=10)

        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=150)

        for event_id, event in my_events.items():
            start_date = datetime.strptime(event['start_date'], "%Y-%m-%d %H:%M")
            tree.insert("", "end", values=(
                event['title'],
                start_date.strftime('%d.%m.%Y'),
                event['location'],
                event['current_participants'],
                event['scanned_count']
            ), tags=(event_id,))

        tree.pack(fill=tk.BOTH, expand=True)

        tree.bind("<Double-1>", self.on_event_double_click)

    def create_event(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        tk.Label(self.content_frame, text="Создание нового мероприятия",
                 font=("Arial", 14)).pack(pady=10)

        form_frame = tk.Frame(self.content_frame)
        form_frame.pack(pady=10)

        fields = [
            ("Название", "title"),
            ("Описание", "description"),
            ("Дата начала (ГГГГ-ММ-ДД ЧЧ:ММ)", "start_date"),
            ("Дата окончания (ГГГГ-ММ-ДД ЧЧ:ММ)", "end_date"),
            ("Место проведения", "location"),
            ("Категории (через ;)", "categories"),
        ]

        self.entry_vars = {}
        for i, (label, field) in enumerate(fields):
            tk.Label(form_frame, text=label).grid(row=i, column=0, sticky="e", padx=5, pady=5)
            entry = tk.Entry(form_frame, width=40)
            entry.grid(row=i, column=1, padx=5, pady=5)
            self.entry_vars[field] = entry

        tk.Button(form_frame, text="Создать мероприятие",
                  command=self.save_new_event).grid(row=len(fields), column=1, pady=10)

    def save_new_event(self):
        new_event = {
            'title': self.entry_vars['title'].get(),
            'description': self.entry_vars['description'].get(),
            'start_date': self.entry_vars['start_date'].get(),
            'end_date': self.entry_vars['end_date'].get(),
            'location': self.entry_vars['location'].get(),
            'categories': self.entry_vars['categories'].get().split(';'),
            'organizer': self.user_data['full_name'],
            'organizer_login': self.user_data['login'],
            'current_participants': 1,
            'scanned_count': 1
        }

        if not all(new_event.values()):
            messagebox.showerror("Ошибка", "Все поля должны быть заполнены")
            return

        new_id = max(events.keys(), default=0) + 1

        events[new_id] = new_event

        self.save_events_to_csv()

        messagebox.showinfo("Успех", "Мероприятие успешно создано!")
        self.show_my_events()

    def save_events_to_csv(self):
        """Сохраняет мероприятия в CSV файл"""
        try:
            with open("events.csv", 'w', encoding='utf-8', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(['id', 'title', 'description', 'start_date', 'end_date',
                                 'location', 'categories', 'organizer', 'organizer_login', 'scanned_count'])

                for event_id, event in events.items():
                    writer.writerow([
                        event_id,
                        event['title'],
                        event['description'],
                        event['start_date'],
                        event['end_date'],
                        event['location'],
                        ';'.join(event['categories']),
                        event['organizer'],
                        event['organizer_login'],
                        event['scanned_count']
                    ])
        except Exception as e:
            print(f"Ошибка при сохранении мероприятий: {e}")

    def show_statistics(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        tk.Label(self.content_frame, text="Статистика мероприятий",
                 font=("Arial", 14)).pack(pady=10)

        my_events = {id: event for id, event in events.items()
                     if event.get('organizer_login') == self.user_data['login']}

        if not my_events:
            tk.Label(self.content_frame, text="У вас пока нет мероприятий").pack(pady=20)
            return

        stats_frame = tk.Frame(self.content_frame)
        stats_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        total_events = len(my_events)
        total_registered = sum(event['current_participants'] for event in my_events.values())
        total_scanned = sum(event['scanned_count'] for event in my_events.values())

        tk.Label(stats_frame, text=f"Всего мероприятий: {total_events}",
                 font=("Arial", 12)).pack(anchor="w", pady=5)
        tk.Label(stats_frame, text=f"Всего регистраций: {total_registered}",
                 font=("Arial", 12)).pack(anchor="w", pady=5)
        tk.Label(stats_frame, text=f"Всего посещений: {total_scanned}",
                 font=("Arial", 12)).pack(anchor="w", pady=5)

        for event_id, event in my_events.items():
            event_frame = tk.Frame(stats_frame, relief=tk.GROOVE, borderwidth=1, padx=10, pady=10)
            event_frame.pack(fill=tk.X, pady=5)

            tk.Label(event_frame, text=event['title'], font=("Arial", 11, "bold")).pack(anchor="w")
            tk.Label(event_frame,
                     text=f"Зарегистрировано: {event['current_participants']}").pack(
                anchor="w")
            tk.Label(event_frame, text=f"Посещения: {event['scanned_count']}").pack(anchor="w")

    def on_event_double_click(self, event):
        item = event.widget.selection()[0]
        event_id_str = event.widget.item(item, "tags")[0]  # Получаем как строку
        event_id = int(event_id_str)  # Преобразуем в число
        self.show_event_details(event_id)

    def show_event_details(self, event_id):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        event = events[event_id]

        tk.Label(self.content_frame, text=event['title'],
                 font=("Arial", 16, "bold")).pack(pady=10)

        info_frame = tk.Frame(self.content_frame)
        info_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        start_date = datetime.strptime(event['start_date'], "%Y-%m-%d %H:%M")
        end_date = datetime.strptime(event['end_date'], "%Y-%m-%d %H:%M")
        date_text = f"Дата и время: {start_date.strftime('%d.%m.%Y %H:%M')} - {end_date.strftime('%d.%m.%Y %H:%M')}"
        tk.Label(info_frame, text=date_text, font=("Arial", 11)).pack(anchor="w", pady=5)

        tk.Label(info_frame, text=f"Место: {event['location']}",
                 font=("Arial", 11)).pack(anchor="w", pady=5)

        categories_text = f"Категории: {', '.join(event['categories'])}"
        tk.Label(info_frame, text=categories_text,
                 font=("Arial", 11)).pack(anchor="w", pady=5)

        stats_text = f"Статистика: {event['current_participants']} зарегистрировано, {event['scanned_count']} посещений"
        tk.Label(info_frame, text=stats_text,
                 font=("Arial", 11)).pack(anchor="w", pady=5)

        button_frame = tk.Frame(info_frame)
        button_frame.pack(pady=20)

        tk.Button(info_frame, text="Назад к списку",
                  command=self.show_my_events).pack(pady=10)

        tk.Button(button_frame, text="Отменить мероприятие", bg="#ff6b6b", fg="white",
                 command=lambda: self.confirm_delete_event(event_id)).pack(side=tk.LEFT, padx=5)

    def confirm_delete_event(self, event_id):
        """Подтверждение удаления мероприятия"""
        event = events[event_id]

        result = messagebox.askyesno(
            "Подтверждение удаления",
            f"Вы уверены, что хотите отменить мероприятие?\n\n"
            f"Название: {event['title']}\n"
            f"Дата: {event['start_date']}\n\n"
            f"Это действие нельзя отменить!",
            icon='warning'
        )

        if result:
            self.delete_event(event_id)

    def delete_event(self, event_id):
        """Удаляет мероприятие"""
        try:
            if event_id in events:
                del events[event_id]

            success = delete_event_from_csv(event_id)

            if success:
                messagebox.showinfo("Успех", "Мероприятие успешно отменено и удалено!")
                self.remove_event_registrations(event_id)
                self.show_my_events()
            else:
                messagebox.showerror("Ошибка", "Не удалось удалить мероприятие из файла")

        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при удалении мероприятия: {e}")

    def remove_event_registrations(self, event_id):
        """Удаляет все регистрации на отмененное мероприятие"""
        try:
            keys_to_remove = [key for key in registrations.keys() if key[1] == event_id]
            for key in keys_to_remove:
                del registrations[key]

            self.update_registrations_file()

        except Exception as e:
            print(f"Ошибка при удалении регистраций: {e}")

    def update_registrations_file(self):
        """Обновляет файл регистраций после удаления"""
        try:
            with open("registrations.csv", 'w', encoding='utf-8', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(['user_login', 'event_id', 'status'])

                for (user_login, event_id), data in registrations.items():
                    writer.writerow([user_login, event_id, data['status']])

        except Exception as e:
            print(f"Ошибка при обновлении регистраций: {e}")

    def go_back(self):
        self.window.destroy()
        self.parent.deiconify()


class ModeratorWindow:
    def __init__(self, parent, user_data):
        self.parent = parent
        self.user_data = user_data
        self.window = tk.Toplevel(parent)
        self.window.title("Панель модератора")
        self.window.geometry("1000x700")
        self.window.protocol("WM_DELETE_WINDOW", self.go_back)

        tk.Label(self.window, text="Панель модератора - Управление пользователями",
                 font=("Arial", 16, "bold")).pack(pady=20)

        search_frame = tk.Frame(self.window)
        search_frame.pack(pady=10)

        tk.Label(search_frame, text="Поиск пользователя:").pack(side=tk.LEFT, padx=5)
        self.search_var = tk.StringVar()
        search_entry = tk.Entry(search_frame, textvariable=self.search_var, width=30)
        search_entry.pack(side=tk.LEFT, padx=5)
        search_entry.bind("<KeyRelease>", self.filter_users)

        columns = ("Логин", "ФИО", "Роль", "Подтвержден", "Категории")
        self.tree = ttk.Treeview(self.window, columns=columns, show="headings", height=20)

        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150)

        scrollbar = ttk.Scrollbar(self.window, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        button_frame = tk.Frame(self.window)
        button_frame.pack(pady=10)

        tk.Button(button_frame, text="Редактировать категории",
                  command=self.edit_categories, width=20).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Изменить статус подтверждения",
                  command=self.toggle_verification, width=25).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Обновить данные",
                  command=self.load_users, width=15).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Назад",
                  command=self.go_back, width=10).pack(side=tk.LEFT, padx=5)

        self.load_users()

    def load_users(self):
        """Загружает пользователей из CSV и обновляет таблицу"""
        global users
        users = load_users_from_csv()

        for item in self.tree.get_children():
            self.tree.delete(item)

        for login, user_data in users.items():
            if user_data['role'] != 'moderator':
                self.tree.insert("", "end", values=(
                    login,
                    user_data['full_name'],
                    user_data['role'],
                    "Да" if user_data['verified'] else "Нет",
                    "; ".join(user_data['categories']) if user_data['categories'] else "Нет категорий"
                ), tags=(login,))

    def filter_users(self, event=None):
        """Фильтрует пользователей по поисковому запросу"""
        search_term = self.search_var.get().lower()

        for item in self.tree.get_children():
            self.tree.delete(item)

        for login, user_data in users.items():
            if (user_data['role'] != 'moderator' and
                    (search_term in login.lower() or
                     search_term in user_data['full_name'].lower() or
                     search_term in user_data['role'].lower() or
                     any(search_term in cat.lower() for cat in user_data['categories']))):
                self.tree.insert("", "end", values=(
                    login,
                    user_data['full_name'],
                    user_data['role'],
                    "Да" if user_data['verified'] else "Нет",
                    "; ".join(user_data['categories']) if user_data['categories'] else "Нет категорий"
                ), tags=(login,))

    def edit_categories(self):
        """Редактирует категории выбранного пользователя"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите пользователя для редактирования")
            return

        login = self.tree.item(selected[0], "tags")[0]
        user_data = users[login]

        edit_window = tk.Toplevel(self.window)
        edit_window.title(f"Редактирование категорий: {user_data['full_name']}")
        edit_window.geometry("1000x700")

        tk.Label(edit_window, text=f"Пользователь: {user_data['full_name']} ({login})",
                 font=("Arial", 12)).pack(pady=10)

        all_categories = ["студенты вузов", "сельская молодёжь", "молодые ветераны СВО"]

        tk.Label(edit_window, text="Доступные категории:",
                 font=("Arial", 10, "bold")).pack(pady=(10, 5), anchor="w")

        self.category_vars = {}
        category_frame = tk.Frame(edit_window)
        category_frame.pack(fill=tk.X, padx=20, pady=5)

        for i, category in enumerate(all_categories):
            var = tk.BooleanVar(value=category in user_data['categories'])
            self.category_vars[category] = var

            cb = tk.Checkbutton(category_frame, text=category, variable=var,
                                font=("Arial", 9))
            cb.grid(row=i // 2, column=i % 2, sticky="w", padx=5, pady=2)

        button_frame = tk.Frame(edit_window)
        button_frame.pack(pady=20)

        tk.Button(button_frame, text="Сохранить",
                  command=lambda: self.save_categories(login, edit_window)).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Отмена",
                  command=edit_window.destroy).pack(side=tk.LEFT, padx=5)

    def save_categories(self, login, edit_window):
        """Сохраняет изменения категорий пользователя"""
        try:
            selected_categories = [cat for cat, var in self.category_vars.items() if var.get()]

            users[login]['categories'] = selected_categories

            self.save_users_to_csv()

            messagebox.showinfo("Успех", "Категории пользователя успешно обновлены!")
            edit_window.destroy()
            self.load_users()

        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить изменения: {e}")

    def toggle_verification(self):
        """Изменяет статус подтверждения пользователя"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите пользователя")
            return

        login = self.tree.item(selected[0], "tags")[0]
        user_data = users[login]

        new_status = not user_data['verified']
        status_text = "подтвержден" if new_status else "не подтвержден"

        result = messagebox.askyesno(
            "Подтверждение",
            f"Вы уверены, что хотите изменить статус пользователя {user_data['full_name']} на '{status_text}'?"
        )

        if result:
            try:
                users[login]['verified'] = new_status

                self.save_users_to_csv()

                messagebox.showinfo("Успех", f"Статус пользователя успешно изменен на '{status_text}'!")
                self.load_users()

            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось изменить статус: {e}")

    def save_users_to_csv(self):
        """Сохраняет пользователей в CSV файл"""
        try:
            with open("users.csv", 'w', encoding='utf-8', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(['login', 'password', 'role', 'full_name', 'verified', 'categories'])

                for login, user_data in users.items():
                    writer.writerow([
                        login,
                        user_data['password'],
                        user_data['role'],
                        user_data['full_name'],
                        str(user_data['verified']).lower(),
                        ';'.join(user_data['categories']) if user_data['categories'] else ''
                    ])
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить данные: {e}")

    def go_back(self):
        self.window.destroy()
        self.parent.deiconify()


class MainWindow:
    def __init__(self, role, login, user_data):
        self.root = tk.Tk()
        self.root.title("Главное меню")
        self.root.geometry("1000x700")
        #self.root.attributes('-fullscreen', True)
        self.login = login
        self.role = role
        self.user_data = user_data

        greetings = {
            "user": "Добро пожаловать, Пользователь!",
            "organizer": "Добро пожаловать, Организатор!",
            "moderator": "Добро пожаловать, Модератор!"
        }

        tk.Label(self.root, text=greetings[role], font=("Arial", 14)).pack(pady=20)

        if role == "user":
            self.user_interface()
        elif role == "organizer":
            self.organizer_interface()
        elif role == "moderator":
            self.moderator_interface()

    def user_interface(self):
        tk.Button(self.root, text="Мой профиль", width=20,
                  command=lambda: self.open_profile(self.login)).pack(pady=5)
        tk.Button(self.root, text="Мероприятия", width=20, command=self.open_events).pack(pady=5)
        tk.Button(self.root, text="Выйти", width=20, command=self.root.destroy).pack(pady=10)

    def organizer_interface(self):
        tk.Button(self.root, text="Управление", width=20,
                 command=self.open_organizer_panel).pack(pady=5)
        tk.Button(self.root, text="Мой профиль", width=20,
                 command=lambda: self.open_profile(self.login)).pack(pady=5)
        tk.Button(self.root, text="Выйти", width=20, command=self.root.destroy).pack(pady=10)

    def moderator_interface(self):
        tk.Button(self.root, text="Управление", width=20,
                 command=self.open_moderator_panel).pack(pady=5)
        tk.Button(self.root, text="Мой профиль", width=20,
                 command=lambda: self.open_profile(self.login)).pack(pady=5)
        tk.Button(self.root, text="Выйти", width=20,
                 command=self.root.destroy).pack(pady=10)

    def open_profile(self, login):
        self.root.withdraw()
        ProfileWindow(self.root, self.login)

    def open_events(self):
        self.root.withdraw()
        EventsWindow(self.root, self.user_data)

    def open_organizer_panel(self):
        self.root.withdraw()
        OrganizerWindow(self.root, self.user_data)

    def open_moderator_panel(self):
        self.root.withdraw()
        ModeratorWindow(self.root, self.user_data)

    def run(self):
        self.root.mainloop()


def count_category_matches(event_categories, user_categories):
    """Подсчитывает количество совпадений категорий мероприятия с категориями пользователя"""
    return sum(1 for category in event_categories if category in user_categories)


if __name__ == "__main__":
    login_app = LoginWindow()
    login_app.run()