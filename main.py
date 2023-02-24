from kivy.app import App
from kivy.uix.widget import Widget
from kivy.properties import ObjectProperty, ListProperty
from kivy.uix.image import Image
from kivy.core.window import Window
from pipe import Pipe
from random import randint

class Background(Widget):
    cloud_texture = ObjectProperty(None)
    tiles_texture = ObjectProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cloud_texture = Image(source='./files/c.png').texture
        self.cloud_texture.wrap = 'repeat'
        self.cloud_texture.uvsize = (Window.width / self.cloud_texture.width, -1)

        self.tiles_texture = Image(source='./files/t.png').texture
        self.tiles_texture.wrap = 'repeat'
        self.tiles_texture.uvsize = (Window.width / self.tiles_texture.width, -1)

    def scroll_textures(self, time_passed):
        # update the position of the texture
        self.cloud_texture.uvpos = (
            (self.cloud_texture.uvpos[0] + (time_passed / 2.0) % Window.width), self.cloud_texture.uvpos[1]
        )
        self.tiles_texture.uvpos = (
            (self.tiles_texture.uvpos[0] + (time_passed / 2.0) % Window.width), self.tiles_texture.uvpos[1]
        )
        # update the texture
        texture = self.property('cloud_texture')
        texture.dispatch(self)
        texture = self.property('tiles_texture')
        texture.dispatch(self)

    pass


from kivy.clock import Clock
from kivy.properties import NumericProperty


class Bird(Image):
    velocity = NumericProperty(0)

    def on_touch_down(self, touch):
        self.source = './files/downflap.png'
        self.velocity = 150
        super().on_touch_down(touch)

    def on_touch_up(self, touch):
        self.source = './files/upflap.png'
        super().on_touch_up(touch)


class MainApp(App):
    pipes = []
    GRAVITY = 300
    was_colliding = False

    # def on_start(self):
    #     Clock.schedule_interval(self.root.ids.background.scroll_textures, 1 / 60.)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def move_bird(self, time_passed):
        bird = self.root.ids.bird
        bird.y = bird.y + bird.velocity * time_passed
        bird.velocity = bird.velocity - self.GRAVITY * time_passed
        self.check_collision()

    def check_collision(self):
        bird = self.root.ids.bird
        is_colliding = False
        for p in self.pipes:
            if p.collide_widget(bird):
                is_colliding = True
                if bird.y < (p.pipe_center - p.GAP_SIZE / 2.0):
                    self.game_over()
                if bird.top > (p.pipe_center + p.GAP_SIZE / 2.0):
                    self.game_over()
            if bird.y < 224:
                self.game_over()
            if bird.top > Window.height:
                self.game_over()
            if self.was_colliding and not is_colliding:
                self.root.ids.score.text = str(int(self.root.ids.score.text) + 1)
            self.was_colliding = is_colliding

    def game_over(self):
        self.root.ids.bird.pos = (20, (self.root.height - 224) / 2.0)
        for p in self.pipes:
            self.root.remove_widget(p)
        self.frames.cancel()
        self.root.ids.start_game_btn.disabled = False
        self.root.ids.start_game_btn.opacity = 1

    def next_frame(self, time_passed):
        self.move_bird(time_passed)
        self.move_pipes(time_passed)
        self.root.ids.background.scroll_textures(time_passed)

    def disable_button(self):
        button = self.root.ids.start_game_btn
        button.disabled = True
        button.opacity = 0

    def start_game(self):
        self.root.ids.score.text = '0'
        self.was_colliding =  False
        self.pipes = []
        # Clock.schedule_interval(self.move_bird, 1 / 60.)
        self.frames = Clock.schedule_interval(self.next_frame, 1 / 60.)
        num_pipes = 5
        distance_between_pipes = Window.width / (num_pipes - 1)
        for i in range(num_pipes):
            pipe = Pipe()
            pipe.pipe_center = randint(224 + 100, self.root.height - 100)
            pipe.size_hint = (None, None)
            pipe.pos = (Window.width + i * distance_between_pipes, 224)
            pipe.size = (64, self.root.height - 224)
            self.pipes.append(pipe)
            self.root.add_widget(pipe)

        # Clock.schedule_interval(self.move_pipes, 1 / 60.)

    def move_pipes(self, time_passed):
        for pipe in self.pipes:
            pipe.x -= time_passed * 100
        num_pipes = 5
        distance_between_pipes = Window.width / (num_pipes - 1)
        list_pipe_x = list(map(lambda p: p.x, self.pipes))
        right_most_pipe_x_pos = max(list_pipe_x)
        if right_most_pipe_x_pos <= Window.width - distance_between_pipes:
            left_most_pipe = self.pipes[list_pipe_x.index(min(list_pipe_x))]
            left_most_pipe.x = Window.width


app = MainApp()
app.run()
