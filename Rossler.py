import numpy as np  # Import NumPy
from scipy.integrate import odeint  # Import odeint

#Define Rossler flow velocity function

#Parameters:
a = 0.2
b = 0.2
c = 5.7


def Velocity(ssp, t):
    """
    Velocity function for the Rossler flow

    Inputs:
    ssp: State space vector. dx1 NumPy array: ssp=[x, y, z]
    t: Time. Has no effect on the function, we have it as an input so that our
       ODE would be compatible for use with generic integrators from
       scipy.integrate

    Outputs:
    vel: velocity at ssp. dx1 NumPy array: vel = [dx/dt, dy/dt, dz/dt]
    """

    x, y, z = ssp  # Read state space points
    # Rossler flow equations:
    dxdt = - y - z
    dydt = x + a * y
    dzdt = b + z * (x - c)
    # Collect Rossler flow equations in a single NumPy array:
    vel = np.array([dxdt, dydt, dzdt], float)  # Velocity vector
    return vel


def Flow(ssp0, deltat):
    """
    Lagrangian description of the flow:
    This function integrates Rossler equation starting at ssp0 for deltat, and
    returns the final state space point.
    Inputs:
    ssp0: Initial state space point
    deltat: Integration time
    Outputs:
    sspdeltat: Final state space point
    """
    # Following numerical integration will return a 2 by 3(=d) solution array
    # where first row contains initial point ssp0, and the last row contains
    # final point
    sspSolution = odeint(Velocity, ssp0, [0.0, deltat])
    sspdeltat = sspSolution[-1, :]  # Read the final point to sspdeltat
    return sspdeltat


def StabilityMatrix(ssp):
    """
    Stability matrix for the Rossler flow

    Inputs:
    ssp: State space vector. dx1 NumPy array: ssp = [x, y, z]
    Outputs:
    A: Stability matrix evaluated at ssp. dxd NumPy array
       A[i, j] = del Velocity[i] / del ssp[j]
    """

    x, y, z = ssp  # Read state space points

    A = np.array([[0, -1, -1],
                  [1, a, 0],
                  [z, 0, x-c]], float)
    return A


def JacobianVelocity(sspJacobian, t):
    """
    Velocity function for the Jacobian integration

    Inputs:
    sspJacobian: (d+d^2)x1 dimensional state space vector including both the
                 state space itself and the tangent space
    t: Time. Has no effect on the function, we have it as an input so that our
       ODE would be compatible for use with generic integrators from
       scipy.integrate

    Outputs:
    velJ = (d+d^2)x1 dimensional velocity vector
    """
    ssp = sspJacobian[0:3]  # First three elements form the original state
                            # space vector
    J = sspJacobian[3:].reshape((3, 3))  # Last nine elements corresponds to
                                         # the elements of Jacobian

    velJ = np.zeros(np.size(sspJacobian))  # Initiate the velocity vector as a
                                           # vector of same size with
                                           # sspJacobian
    velJ[0:3] = Velocity(ssp, t)
    # Last dxd elements of the velJ are determined by the action of
    # stability matrix on the current value of the Jacobian
    velTangent = np.dot(StabilityMatrix(ssp), J)  # Velocity matrix for
                                                  # the tangent space
    velJ[3:] = np.reshape(velTangent, 9)  # Another use of numpy.reshape, here
                                          # to convert from dxd to d^2
    return velJ


def Jacobian(ssp, t):
    """
    Jacobian function for the trajectory started on ssp, evolved for time t

    Inputs:
    ssp: Initial state space point. dx1 NumPy array: ssp = [x, y, z]
    t: Integration time
    Outputs:
    J: Jacobian of trajectory f^t(ssp). dxd NumPy array
    """
    J0 = np.identity(3)
    # Initial condition for Jacobian integral is a d+d^2 dimensional matrix
    # formed by concatenation of initial condition for state space and the
    # Jacobian
    sspJacobian0 = np.zeros(3 + 3 ** 2)
    sspJacobian0[0:3] = ssp
    sspJacobian0[3:] = np.reshape(J0, 9)

    tInitial = 0  # Initial time
    tFinal = t    # Final time
    Nt = t * 100  # Number of time points to be used in the integration
    tArray = np.linspace(tInitial, tFinal, Nt)  # Time array for solution

    sspJacobianSolution = odeint(JacobianVelocity, sspJacobian0, tArray)

    # Read the Jacobian for the periodic orbit
    J = sspJacobianSolution[-1, 3:].reshape((3, 3))
    return J


if __name__ == "__main__":
    # This block will be evaluated if this script is called as the main routine
    # and will be ignored if this file is imported from another script.

    import RungeKutta as rk

    tInitial = 0  # Initial time
    # tFinal = 100  # Final time
    tFinal = 2  # Final time
    # tFinal = 5.881088455554846384
    Nt = 10000  # Number of time points to be used in the integration

    tArray = np.linspace(tInitial, tFinal, Nt)  # Time array for solution
    ssp0 = np.array([9.269083709793489945,
                     0.0,
                     2.581592405683282632], float)  # Initial condition for the solution
    # ssp0 = np.array([1.0,
    #                  1.0,
    #                  1.0], float)  # Initial condition for the solution

    # sspSolution = rk.RK4(Velocity, ssp0, tArray)
    sspSolution = odeint(Velocity, ssp0, tArray)

    xt = sspSolution[:, 0]  # Read x(t)
    yt = sspSolution[:, 1]  # Read y(t)
    zt = sspSolution[:, 2]  # Read z(t)

    print((xt[-1], yt[-1], zt[-1]))  # Print final point

    #Import plotting functions:
    import matplotlib as mpl
    from mpl_toolkits.mplot3d import Axes3D
    import matplotlib.pyplot as plt

    fig = plt.figure()  # Create a figure instance
    ax = fig.gca(projection='3d')  # Get current axes in 3D projection
    ax.plot(xt, yt, zt)  # Plot the solution
    ax.set_xlabel('x')  # Set x label
    ax.set_ylabel('y')  # Set y label
    ax.set_zlabel('z')  # Set z label
    plt.show()  # Show the figure