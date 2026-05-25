import pygame
import Mundo
import objetos
import slots

pygame.init()

tela = pygame.display.set_mode((1050, 640))

clock = pygame.time.Clock()

rodando = True

bonk = objetos.Objetos(100,100, pygame.image.load('jogo-pygame/imagens/image.png').convert_alpha(), 1)
bonk2 = objetos.Objetos(350,100, pygame.image.load('jogo-pygame/imagens/image2.png').convert_alpha(), 2)
bonk3 = objetos.Objetos(600,100, pygame.image.load('jogo-pygame/imagens/image3.png').convert_alpha(), 3)

mundo = Mundo.Mundo()
mundo.add_obj(bonk)
mundo.add_obj(bonk2)
mundo.add_obj(bonk3)

slot1 = slots.Slot(100,100,200,50, 1)
slot2 = slots.Slot(350,100,200,50, 2)
slot3 = slots.Slot(600,100,200,50, 3)

slots = [slot1, slot2, slot3]


def verificar(slots):

    for slot in slots:

        if slot.item is None:
            return False

        if slot.item.valor != slot.resposta:
            return False

    return True

while rodando:

    tela.fill((0,0,0))

    mouse = pygame.mouse.get_pos()
    mundo.update()
    mundo.draw(tela)
    for slot in slots:
        slot.draw(tela)

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            rodando = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse = pygame.mouse.get_pos()

            mundo.clicar(mouse)

            if verificar(slots):
                print("CERTO")

        if event.type == pygame.MOUSEBUTTONUP:
            if mundo.obj_selecionado:

                for slot in slots:

                    if slot.rect.colliderect(mundo.obj_selecionado.rect):

                        slot.item = mundo.obj_selecionado

                        mundo.obj_selecionado.x = slot.rect.x
                        mundo.obj_selecionado.y = slot.rect.y

                        mundo.obj_selecionado.update()

                        break

            mundo.soltar()

        if event.type == pygame.MOUSEMOTION:
            mundo.mover(mouse)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
