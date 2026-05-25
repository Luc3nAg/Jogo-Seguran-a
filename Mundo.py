class Mundo:
    def __init__(self):
        self.objetos = []
        self.obj_selecionado = None

    def add_obj(self, obj):
        self.objetos.append(obj)

    def remove_obj(self, obj):
        self.objetos.remove(obj)

    def update(self):
        for obj in self.objetos:
            obj.update()

    def draw(self, surface): 
        for obj in self.objetos:
            obj.draw(surface)

    def clicar(self, pos):

        for obj in reversed(self.objetos):

            if obj.rect.collidepoint(pos):

                self.obj_selecionado = obj

                obj.arrastando = True

                self.objetos.remove(obj)
                self.objetos.append(obj)

                break

    def soltar(self):

        if self.obj_selecionado:
            self.obj_selecionado.arrastando = False
            self.obj_selecionado = None

    def mover(self, pos):

        if self.obj_selecionado:

            self.obj_selecionado.x = pos[0]
            self.obj_selecionado.y = pos[1]