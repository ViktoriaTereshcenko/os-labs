import java.util.concurrent.Semaphore;
import java.util.concurrent.locks.Lock;
import java.util.concurrent.locks.ReentrantLock;
import java.util.Random;

public class DiningPhilosophers {

    private static final int N = 5;  // кількість філософів (і виделок)

    enum State {   // стани філософів
        THINKING,
        HUNGRY,
        EATING
    }

    private State[] state = new State[N];  // масив для відстеження стану кожного філософа
    private final Lock criticalRegionLock = new ReentrantLock();  // для критичних регіонів
    private final Lock outputLock = new ReentrantLock();  // для синхронізованого виведення
    private final Semaphore[] bothForksAvailable = new Semaphore[N];  // один семафор на філософа

    private final Random rand = new Random();

    public DiningPhilosophers() {
        for (int i = 0; i < N; i++) {
            state[i] = State.THINKING;
            bothForksAvailable[i] = new Semaphore(0);  // спочатку виделки відсутні
        }
    }

    private int left(int i) {
        return (i + N - 1) % N;
    }

    private int right(int i) {
        return (i + 1) % N;
    }

    private int myRand(int min, int max) {
        return rand.nextInt((max - min) + 1) + min;
    }

    private void test(int i) {
        if (state[i] == State.HUNGRY &&
                state[left(i)] != State.EATING &&
                state[right(i)] != State.EATING) {
            state[i] = State.EATING;
            bothForksAvailable[i].release();  // дозвіл філософу їсти
        }
    }

    private void think(int i) {
        int duration = myRand(400, 800);
        outputLock.lock();
        try {
            System.out.println("Philosopher " + i + " is THINKING " + duration + "ms");
        } finally {
            outputLock.unlock();
        }
        try {
            Thread.sleep(duration);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
    }

    private void takeForks(int i) {
        criticalRegionLock.lock();
        try {
            state[i] = State.HUNGRY;
            outputLock.lock();
            try {
                System.out.println("Philosopher " + i + " is HUNGRY");
            } finally {
                outputLock.unlock();
            }
            // Якщо прибрати test(i), філософи не перевірятимуть одразу обидві виделки,
            // а братимуть одну та чекатимуть на іншу. Це призведе до дедлоку
            test(i);
        } finally {
            criticalRegionLock.unlock();
        }
        try {
            bothForksAvailable[i].acquire();  // блокуємо, якщо виделки не були отримані
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
    }

    private void eat(int i) {
        int duration = myRand(400, 800);
        outputLock.lock();
        try {
            System.out.println("Philosopher " + i + " is EATING " + duration + "ms");
        } finally {
            outputLock.unlock();
        }
        try {
            Thread.sleep(duration);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
    }

    private void putForks(int i) {
        criticalRegionLock.lock();
        try {
            state[i] = State.THINKING;
            test(left(i));
            test(right(i));
        } finally {
            criticalRegionLock.unlock();
        }
    }

    public void philosopher(int i) {
        while (true) {
            think(i);
            takeForks(i);
            eat(i);
            putForks(i);
        }
    }

    public static void main(String[] args) {
        DiningPhilosophers dp = new DiningPhilosophers();

        Thread[] philosophers = new Thread[N];
        for (int i = 0; i < N; i++) {
            final int index = i;
            philosophers[i] = new Thread(() -> dp.philosopher(index));
            philosophers[i].start();
        }
    }
}
