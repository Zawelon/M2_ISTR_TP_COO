# Create your models here.
from django.db import models
from datetime import timedelta


######################CLASS Ville################
class Ville(models.Model):
    nom = models.CharField(max_length=100)
    code_postal = models.IntegerField(default=0)
    prix_par_m2 = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.nom

    def json(self):
        return {
            "ID": self.id,
            "Nom": self.nom,
            "Code_postal": self.code_postal,
            "Prix_par_metre_carre": str(self.prix_par_m2),
        }

    def json_extended(self):
        return self.json()


######################CLASS Local################
class Local(models.Model):
    nom = models.CharField(max_length=100)
    ville = models.ForeignKey(Ville, on_delete=models.CASCADE)
    surface = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.nom

    def json(self):
        return {
            "ID": self.id,
            "Nom": self.nom,
            "Ville": self.ville.nom,
            "Surface": str(self.surface),
        }

    def json_extended(self):
        return {
            "Nom": self.nom,
            "Ville": self.ville.json_extended(),
            "Surface": str(self.surface),
        }


######################CLASS SiegeSocial################
class SiegeSocial(Local):
    pass


######################CLASS Machine################
class Machine(models.Model):
    nom = models.CharField(max_length=100)
    prix = models.DecimalField(max_digits=10, decimal_places=2)
    n_serie = models.CharField(max_length=100)

    def costs(self):
        return self.prix

    def __str__(self):
        return self.nom

    def json(self):
        return {
            "ID": self.id,
            "nom": self.nom,
            "prix": str(self.prix),
            "numero_de_serie": self.n_serie,
        }

    def json_extended(self):
        return self.json()


######################CLASS Usine################
class Usine(Local):
    machines = models.ManyToManyField(Machine)

    def __str__(self):
        return self.nom

    def costs(self):
        area_cost = self.surface * self.ville.prix_par_m2
        machines_cost = sum(machine.costs() for machine in self.machines.all())
        stock_cost = sum(stock.costs() for stock in self.stock_set.all())
        return area_cost + machines_cost + stock_cost

    def json(self):
        return {
            "ID": self.id,
            "nom": self.nom,
            "surface": str(self.surface),
            "ville": self.ville.nom,
        }

    def json_extended(self):
        return {
            "nom": self.nom,
            "surface": str(self.surface),
            "ville": self.ville.json_extended(),
            "machines": [machine.json_extended() for machine in self.machines.all()],
            "stock": [stock.json_extended() for stock in self.stock_set.all()],
        }


######################CLASS OBJET################
class Objet(models.Model):
    nom = models.CharField(max_length=100, unique=True)
    prix = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return self.nom

    def json(self):
        return {"ID": self.id, "nom": self.nom, "prix": str(self.prix)}

    def json_extended(self):
        return self.json()


######################CLASS Ressource################
class Ressource(Objet):
    pass


######################CLASS QuantiteRessource##########
class QuantiteRessource(models.Model):
    ressource = models.ForeignKey(Ressource, on_delete=models.CASCADE)
    quantite = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.quantite} de {self.ressource.nom}"

    def costs(self):
        return self.quantite * self.ressource.prix

    def json(self):
        return {
            "ID": self.id,
            "ressource": self.ressource.nom,
            "quantite": self.quantite,
        }

    def json_extended(self):
        return {"ressource": self.ressource.json_extended(), "quantite": self.quantite}


######################CLASS Etape################
class Etape(models.Model):
    nom = models.CharField(max_length=100)
    machine = models.ForeignKey(Machine, on_delete=models.CASCADE)
    quantite_ressource = models.ForeignKey(QuantiteRessource, on_delete=models.CASCADE)
    duree = models.DurationField(default=timedelta())
    etape_suivante = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="precedente",
    )

    def __str__(self):
        return self.nom

    def json(self):
        return {
            "ID": self.id,
            "nom": self.nom,
            "machine": self.machine.nom,
            "quantite_ressource": self.quantite_ressource.json(),
            "duree": self.duree,
            "etape_suivante": self.etape_suivante.nom if self.etape_suivante else None,
        }

    def json_extended(self):
        return {
            "nom": self.nom,
            "machine": self.machine.json_extended(),
            "quantite_ressource": self.quantite_ressource.json_extended(),
            "duree": self.duree,
            "etape_suivante": self.etape_suivante.json_extended()
            if self.etape_suivante
            else None,
        }


######################CLASS Produit################
class Produit(Objet):
    premiere_etape = models.ForeignKey(Etape, on_delete=models.CASCADE)

    def __str__(self):
        return self.nom

    def json(self):
        return {
            "ID": self.id,
            "nom": self.nom,
            "prix": str(self.prix),
            "premiere_etape": self.premiere_etape.nom,
        }

    def json_extended(self):
        return {
            "nom": self.nom,
            "prix": str(self.prix),
            "premiere_etape": self.premiere_etape.json_extended(),
        }


###################### CLASS Stock ################
class Stock(models.Model):
    ressources = models.ManyToManyField(Ressource)
    nombre = models.IntegerField(default=0)
    usine = models.ForeignKey(Usine, on_delete=models.CASCADE)

    def costs(self):
        return sum(ressource.prix * self.nombre for ressource in self.ressources.all())

    def json(self):
        return {
            "ID": self.id,
            "ressources": [
                {"nom": ressource.nom, "nombre": self.nombre}
                for ressource in self.ressources.all()
            ],
            "usine": self.usine.nom,
        }

    def json_extended(self):
        return {
            "ressources": [
                {"nom": ressource.nom, "nombre": self.nombre}
                for ressource in self.ressources.all()
            ],
            "usine": self.usine.json_extended(),
        }
