import configparser
import json
import os
import random
from datetime import datetime
import customtkinter as ctk
from tkinter import filedialog, messagebox

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")
class CCNAQuizMaster(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("CCNA Quiz Master • v2.0")
        self.geometry("1024x768")
        self.minsize(1000, 650)
        # Variables
        self.config = self.load_config()
        self.all_questions = []
        self.session_questions = []
        self.user_answers = []
        self.current_index = 0
        self.score = 0
        self.history = self.load_history()

        # UI principale avec onglets
        self.tabview = ctk.CTkTabview(self, corner_radius=20)
        self.tabview.pack(fill="both", expand=True, padx=20, pady=20)

        self.tab_home = self.tabview.add("Accueil")
        self.tab_stats = self.tabview.add("Statistiques")
        self.tab_profile = self.tabview.add("Profil")

        self.build_home_tab()
        self.build_stats_tab()
        self.build_profile_tab()

        if not self.config:
            self.show_profile_setup()
        else:
            self.update_user_info()

    def load_config(self):
        if os.path.exists("config.json"):
            with open("config.json", "r", encoding="utf-8") as f:
                return json.load(f)
        return None

    def save_config(self):
        with open("config.json", "w", encoding="utf-8") as f:
            json.dump(self.config, f, ensure_ascii=False, indent=2)

    def load_history(self):
        if os.path.exists("historique.json"):
            with open("historique.json", "r", encoding="utf-8") as f:
                return json.load(f)
        return []

    def save_history(self):
        with open("historique.json", "w", encoding="utf-8") as f:
            json.dump(self.history, f, ensure_ascii=False, indent=2)

    def update_user_info(self):
        self.title(f"CCNA Quiz Master • {self.config['prenom']} {self.config['nom']}")

    # ====================== ÉCRAN DE CRÉATION DE PROFIL ======================
    def show_profile_setup(self):
        setup_win = ctk.CTkToplevel(self)
        setup_win.title("Création de Profil")
        setup_win.geometry("500x420")
        setup_win.grab_set()

        ctk.CTkLabel(setup_win, text="Bienvenue dans CCNA Quiz Master", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=20)

        ctk.CTkLabel(setup_win, text="Prénom :").pack(anchor="w", padx=40)
        prenom_entry = ctk.CTkEntry(setup_win, width=400)
        prenom_entry.pack(pady=5, padx=40)

        ctk.CTkLabel(setup_win, text="Nom :").pack(anchor="w", padx=40)
        nom_entry = ctk.CTkEntry(setup_win, width=400)
        nom_entry.pack(pady=5, padx=40)

        path_var = ctk.StringVar()

        def browse_json():
            file = filedialog.askopenfilename(filetypes=[("Fichiers JSON", "*.json")])
            if file:
                path_var.set(file)

        ctk.CTkButton(setup_win, text="Choisir le fichier questions CCNA (.json)", command=browse_json, width=400).pack(pady=20, padx=40)
        ctk.CTkLabel(setup_win, textvariable=path_var, text_color="lightblue").pack(pady=5)

        def valider():
            if prenom_entry.get().strip() and nom_entry.get().strip() and path_var.get():
                self.config = {
                    "prenom": prenom_entry.get().strip(),
                    "nom": nom_entry.get().strip(),
                    "db_path": path_var.get()
                }
                self.save_config()
                self.update_user_info()
                setup_win.destroy()
                messagebox.showinfo("Succès", f"Profil créé pour {self.config['prenom']} !")
            else:
                messagebox.showerror("Erreur", "Tous les champs sont obligatoires !")

        ctk.CTkButton(setup_win, text="Créer mon profil", command=valider, fg_color="green", height=40, font=ctk.CTkFont(size=16)).pack(pady=30)

    # ====================== ONGLET ACCUEIL ======================
    def build_home_tab(self):
        frame = ctk.CTkFrame(self.tab_home)
        frame.pack(fill="both", expand=True, padx=30, pady=30)

        ctk.CTkLabel(frame, text=f"Bonjour {self.config.get('prenom', 'Utilisateur')} 👋",
                     font=ctk.CTkFont(size=28, weight="bold")).pack(pady=(0, 10))

        ctk.CTkLabel(frame, text="Prêt à progresser en CCNA ?", font=ctk.CTkFont(size=18)).pack(pady=10)

        # Sélection nombre de questions
        ctk.CTkLabel(frame, text="Nombre de questions :", font=ctk.CTkFont(size=16)).pack(anchor="w", pady=(30, 8))

        self.nb_var = ctk.IntVar(value=20)
        values = [10, 20, 30, 40, 50, 100]

        btn_frame = ctk.CTkFrame(frame, fg_color="transparent")
        btn_frame.pack(pady=10)

        for v in values:
            btn = ctk.CTkButton(btn_frame, text=str(v), width=60, height=40,
                                fg_color="gray20" if v != 20 else "blue",
                                command=lambda x=v: self.set_nb_questions(x))
            btn.pack(side="left", padx=5)
            setattr(self, f"nb_btn_{v}", btn)

        # Bouton Lancer
        ctk.CTkButton(frame, text="🚀 LANCER LE QUIZ", height=60, font=ctk.CTkFont(size=20, weight="bold"),
                      command=self.start_quiz).pack(pady=40, padx=100, fill="x")

        # Dernier score
        self.last_score_label = ctk.CTkLabel(frame, text="", font=ctk.CTkFont(size=16))
        self.last_score_label.pack(pady=20)

        self.refresh_last_score()

    def set_nb_questions(self, n):
        self.nb_var.set(n)
        for v in [10, 20, 30, 40, 50, 100]:
            btn = getattr(self, f"nb_btn_{v}")
            btn.configure(fg_color="blue" if v == n else "gray20")

    def start_quiz(self):
        try:
            with open(self.config["db_path"], "r", encoding="utf-8") as f:
                self.all_questions = json.load(f)
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible de charger le fichier JSON :\n{e}")
            return

        if not self.all_questions:
            messagebox.showerror("Erreur", "Le fichier JSON ne contient aucune question.")
            return

        nb = min(self.nb_var.get(), len(self.all_questions))
        self.session_questions = random.sample(self.all_questions, nb)
        self.user_answers = [None] * nb
        self.current_index = 0
        self.score = 0

        self.quiz_window = ctk.CTkToplevel(self)
        self.quiz_window.title("Quiz CCNA en cours")
        self.quiz_window.geometry("1280X800")
        self.quiz_window.grab_set()

        self.build_quiz_ui()

    def build_quiz_ui(self):
        for widget in self.quiz_window.winfo_children():
            widget.destroy()

        q = self.session_questions[self.current_index]

        # En-tête
        header = ctk.CTkFrame(self.quiz_window, height=80)
        header.pack(fill="x", padx=20, pady=20)
        header.pack_propagate(False)

        progress = (self.current_index / len(self.session_questions)) * 100
        ctk.CTkLabel(header, text=f"Question {self.current_index + 1} / {len(self.session_questions)}",
                     font=ctk.CTkFont(size=18, weight="bold")).pack(side="left", padx=20)

        prog_bar = ctk.CTkProgressBar(header, width=500)
        prog_bar.set(progress / 100)
        prog_bar.pack(side="left", padx=20, fill="x", expand=True)

        # Question
        q_frame = ctk.CTkFrame(self.quiz_window)
        q_frame.pack(fill="both", expand=True, padx=40, pady=20)

        ctk.CTkLabel(q_frame, text=q["question"], wraplength=850,
                     font=ctk.CTkFont(size=18), justify="left").pack(pady=30, anchor="w")

        # Propositions
        for prop in q["propositions"]:
            btn = ctk.CTkButton(q_frame, text=prop, height=55, anchor="w",
                                fg_color="gray20", hover_color="blue",
                                command=lambda p=prop: self.select_answer(p))
            btn.pack(pady=8, padx=20, fill="x")

            # Marquer la sélection précédente
            if self.user_answers[self.current_index] == prop:
                btn.configure(fg_color="blue")

        # Navigation
        nav = ctk.CTkFrame(self.quiz_window)
        nav.pack(fill="x", padx=40, pady=20)

        ctk.CTkButton(nav, text="← Précédent", width=150,
                      command=self.prev_question,
                      state="normal" if self.current_index > 0 else "disabled").pack(side="left")

        txt = "Terminer le Quiz" if self.current_index == len(self.session_questions)-1 else "Suivant →"
        ctk.CTkButton(nav, text=txt, width=200, fg_color="green",
                      command=self.next_question).pack(side="right")

    def select_answer(self, choice):
        self.user_answers[self.current_index] = choice
        self.build_quiz_ui()  # Rafraîchir pour montrer la sélection

    def next_question(self):
        if self.current_index < len(self.session_questions) - 1:
            self.current_index += 1
            self.build_quiz_ui()
        else:
            self.finish_quiz()

    def prev_question(self):
        if self.current_index > 0:
            self.current_index -= 1
            self.build_quiz_ui()

    def finish_quiz(self):
        self.score = sum(1 for i, q in enumerate(self.session_questions)
                        if self.user_answers[i] == q["reponse_correcte"])

        percent = round((self.score / len(self.session_questions)) * 100, 1)

        # Sauvegarde historique
        entry = {
            "date": datetime.now().strftime("%d/%m/%Y %H:%M"),
            "total": len(self.session_questions),
            "score": self.score,
            "pourcentage": f"{percent}%"
        }
        self.history.insert(0, entry)
        self.save_history()

        self.quiz_window.destroy()
        self.show_results(percent)

    def show_results(self, percent):
        result_win = ctk.CTkToplevel(self)
        result_win.title("Résultats du Quiz")
        result_win.geometry("1100x750")

        ctk.CTkLabel(result_win, text=f"Score final : {self.score}/{len(self.session_questions)} ({percent}%)",
                     font=ctk.CTkFont(size=32, weight="bold"), text_color="green").pack(pady=30)

        # Tableau détaillé
        scroll = ctk.CTkScrollableFrame(result_win)
        scroll.pack(fill="both", expand=True, padx=40, pady=20)

        for i, q in enumerate(self.session_questions):
            correct = q["reponse_correcte"]
            user = self.user_answers[i]
            is_ok = user == correct

            color = "green" if is_ok else "red"
            icon = "✅" if is_ok else "❌"

            frame = ctk.CTkFrame(scroll)
            frame.pack(fill="x", pady=8, padx=10)

            ctk.CTkLabel(frame, text=f"{icon} Question {i+1}",
                         text_color=color, font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=15, pady=8)
            ctk.CTkLabel(frame, text=q["question"], wraplength=950, justify="left").pack(anchor="w", padx=15)

            ctk.CTkLabel(frame, text=f"Votre réponse : {user or 'Aucune'}",
                         text_color=color).pack(anchor="w", padx=15)
            ctk.CTkLabel(frame, text=f"Réponse correcte : {correct}").pack(anchor="w", padx=15)

        ctk.CTkButton(result_win, text="Retour au menu principal", height=50,
                      command=result_win.destroy).pack(pady=20)

        self.refresh_last_score()
        self.refresh_stats_tab()

    # ====================== ONGLET STATISTIQUES ======================
    def build_stats_tab(self):
        self.stats_frame = ctk.CTkFrame(self.tab_stats)
        self.stats_frame.pack(fill="both", expand=True, padx=35, pady=35)
        self.refresh_stats_tab()

    def refresh_stats_tab(self):
        for widget in self.stats_frame.winfo_children():
            widget.destroy()

        if not self.history:
            ctk.CTkLabel(self.stats_frame, text="Aucun quiz terminé pour le moment.\nLancez votre premier entraînement !",
                         font=ctk.CTkFont(size=18)).pack(pady=100)
            return

        # Statistiques globales
        total_sessions = len(self.history)
        scores = [float(h["pourcentage"].replace("%", "")) for h in self.history]
        avg = round(sum(scores) / total_sessions, 1)
        best = max(scores)

        grid = ctk.CTkFrame(self.stats_frame)
        grid.pack(fill="x", pady=30)

        self.create_stat_card(grid, "Sessions", total_sessions, 0)
        self.create_stat_card(grid, "Moyenne", f"{avg}%", 1)
        self.create_stat_card(grid, "Meilleur", f"{best}%", 2)

        # Historique
        ctk.CTkLabel(self.stats_frame, text="Historique des entraînements",
                     font=ctk.CTkFont(size=20, weight="bold")).pack(anchor="w", pady=(30,10))

        scroll = ctk.CTkScrollableFrame(self.stats_frame)
        scroll.pack(fill="both", expand=True)

        for entry in self.history[:20]:  # 20 derniers
            row = ctk.CTkFrame(scroll)
            row.pack(fill="x", pady=6, padx=10)

            ctk.CTkLabel(row, text=entry["date"], width=180, anchor="w").pack(side="left", padx=10)
            ctk.CTkLabel(row, text=f"{entry['score']}/{entry['total']}", width=100).pack(side="left")
            ctk.CTkLabel(row, text=entry["pourcentage"], text_color="green",
                         font=ctk.CTkFont(weight="bold")).pack(side="left", padx=20)

    def create_stat_card(self, parent, title, value, col):
        card = ctk.CTkFrame(parent, corner_radius=16)
        card.grid(row=0, column=col, padx=15, sticky="ew")
        parent.grid_columnconfigure(col, weight=1)

        ctk.CTkLabel(card, text=title, font=ctk.CTkFont(size=14)).pack(pady=(15,5))
        ctk.CTkLabel(card, text=str(value), font=ctk.CTkFont(size=36, weight="bold")).pack(pady=5)

    # ====================== ONGLET PROFIL ======================
    def build_profile_tab(self):
        frame = ctk.CTkFrame(self.tab_profile)
        frame.pack(fill="both", expand=True, padx=40, pady=40)

        ctk.CTkLabel(frame, text="Modifier votre profil", font=ctk.CTkFont(size=24, weight="bold")).pack(pady=20)

        # Prénom & Nom
        ctk.CTkLabel(frame, text="Prénom").pack(anchor="w", padx=20)
        self.prenom_entry = ctk.CTkEntry(frame, width=400)
        self.prenom_entry.pack(pady=8, padx=20)
        self.prenom_entry.insert(0, self.config.get("prenom", ""))

        ctk.CTkLabel(frame, text="Nom").pack(anchor="w", padx=20)
        self.nom_entry = ctk.CTkEntry(frame, width=400)
        self.nom_entry.pack(pady=8, padx=20)
        self.nom_entry.insert(0, self.config.get("nom", ""))

        # Fichier JSON
        ctk.CTkLabel(frame, text="Fichier de questions").pack(anchor="w", padx=20, pady=(20,5))
        self.db_label = ctk.CTkLabel(frame, text=self.config.get("db_path", "Non défini"), text_color="lightblue")
        self.db_label.pack(anchor="w", padx=20)

        ctk.CTkButton(frame, text="Changer le fichier JSON", command=self.change_json_file).pack(pady=15)

        ctk.CTkButton(frame, text="💾 Enregistrer les modifications", fg_color="green", height=45,
                      command=self.save_profile_changes).pack(pady=40)

        ctk.CTkButton(frame, text="💾 Supprimer Tout", fg_color="green", height=45,
                      command=self.reinit_config).pack(pady=40)

    def change_json_file(self):
        file = filedialog.askopenfilename(filetypes=[("JSON", "*.json")])
        if file:
            self.config["db_path"] = file
            self.db_label.configure(text=file)

    def reinit_config(self):
        self.config= {}
        self.history= {}
        messagebox.showwarning("Attention","Profil, statistiques et historique réinitialisés!!")

    def save_profile_changes(self):
        self.config["prenom"] = self.prenom_entry.get().strip()
        self.config["nom"] = self.nom_entry.get().strip()
        self.save_config()
        self.update_user_info()
        messagebox.showinfo("Succès", "Profil mis à jour !")

    def refresh_last_score(self):
        if not self.history:
            self.last_score_label.configure(text="Aucun quiz terminé")
            return
        last = self.history[0]
        self.last_score_label.configure(
            text=f"Dernier score : {last['score']}/{last['total']}  •  {last['pourcentage']}  •  {last['date']}"
        )

if __name__ == "__main__":
    app = CCNAQuizMaster()
    app.mainloop()