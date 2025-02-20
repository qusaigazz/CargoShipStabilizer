import math

def get_user_input():
    print("Enter the following ship and container parameters:")

    # Ship Parameters
    max_height = float(input("Maximum allowable ship height (m): "))
    max_width = float(input("Maximum allowable ship width (m): "))
    max_draft = float(input("Maximum allowable ship draft (m): "))
    max_length = float(input("Maximum allowable ship length (m): "))

    # Ship Design
    s_width = float(input("Ship width (m): "))
    s_total_height = float(input("Ship total height (m): "))
    s_length = float(input("Ship length (m): "))
    s_draft = float(input("Ship draft (m): "))

    # Container and Capacity Parameters
    container_width = float(input("Width of one container (m) [Default: 2.438]: ") or 2.438)
    container_length = float(input("Length of one container (m) [Default: 6.096]: ") or 6.096)
    capacity = float(input("Capacity utilization factor (0 to 1) [Default: 0.7]: ") or 0.7)
    prismatic_co = float(input("Prismatic coefficient of the ship [Default: 0.85]: ") or 0.85)

    return (max_height, max_width, max_draft, max_length, s_width, s_total_height, s_length, s_draft, container_width, container_length, capacity, prismatic_co)

def find_container_bottom_TEU(s_width, s_total_height, s_length, container_width, container_length, capacity, prismatic_co):
    containers_per_layer = []
    for h in range(0, math.floor(s_total_height), 3):
        number_of_columns = math.floor(s_width / container_width)
        number_of_rows = math.floor(s_length / container_length)
        number_of_containers_per_layer = number_of_columns * number_of_rows
        containers_per_layer.append(number_of_containers_per_layer)
    below_capacity = math.floor(sum(containers_per_layer) * capacity)
    total_capacity = below_capacity * prismatic_co
    return math.floor(total_capacity)

def find_container_upper_TEU(bottom_capacity):
    upper_estimate = bottom_capacity * (0.3 / 0.7)
    return math.floor(upper_estimate)

def find_upper_height(upper_estimate, s_length, container_length, s_width, container_width):
    rows = math.floor(s_length / container_length)
    columns = math.floor(s_width / container_width)
    one_layer = 0.8 * (rows * columns)
    total_layers = math.floor(upper_estimate / one_layer)
    upper_rect_height = total_layers * 3
    return upper_rect_height

def find_center_of_gravity(s_width, s_total_height, s_length, upper_height):
    ship_centroid = s_total_height / 2
    cargo_centroid = s_total_height + (upper_height / 2)
    ship_area = s_width * s_total_height * s_length
    cargo_area = 0.8 * (s_width * upper_height * s_length)
    center_of_gravity = ((ship_centroid * ship_area) + (cargo_centroid * cargo_area)) / (ship_area + cargo_area)
    return center_of_gravity

def find_center_of_buoyancy(s_draft):
    return s_draft / 2

def find_moment_of_inertia(s_width, s_length):
    return (1 / 12) * s_length * (s_width ** 3)

def find_metacentric_height(center_of_buoyancy, center_of_gravity, moment_of_inertia, s_draft, s_width, s_length):
    bg = center_of_buoyancy - center_of_gravity
    bm = moment_of_inertia / (s_draft * s_width * s_length)
    return bm + bg

def stability_check(metacentric_height, s_width, s_length, s_draft, find_upper_height, center_of_buoyancy, moment_of_inertia, max_width, max_length, max_draft, s_total_height):
    height = find_upper_height
    updated_height = height

    while metacentric_height < 0 or metacentric_height > 2.5:
        if metacentric_height < 0:
            new_width = s_width + 2
            new_length = new_width * 4.8

            if new_width <= max_width and new_length <= max_length:
                s_width = new_width
                s_length = new_length
                print(f"Increased ship width to: {s_width} meters")
                print(f"Increased ship length to: {s_length} meters")

            elif s_draft + 0.5 <= max_draft:
                s_draft += 0.5
                print(f"Increased draft to: {s_draft} meters")

            elif height >= 3:
                updated_height = height - 3
                height = updated_height
                print(f"Reduced cargo height to: {updated_height} meters")

            else:
                print("No further modifications possible.")
                break

        elif metacentric_height > 2.5:
            updated_height += 3
            print(f"Increased cargo height to: {updated_height} meters")

        updated_center_of_gravity = find_center_of_gravity(s_width, s_total_height, s_length, updated_height)
        new_metacentric_height = find_metacentric_height(center_of_buoyancy, updated_center_of_gravity, moment_of_inertia, s_draft, s_width, s_length)
        metacentric_height = new_metacentric_height

        if 0.5 <= metacentric_height <= 2.5:
            print("Stability achieved.")
            break

    return metacentric_height, s_width, s_length, s_draft, updated_height

def new_upperdeck_capacity(find_container_upper_TEU, height):
    initial_capacity_upper = find_container_upper_TEU
    containers_per_layer = initial_capacity_upper / 3
    final_capacity = containers_per_layer * (height / 3)
    return math.floor(final_capacity)

def find_full_capacity(new_upperdeck_capacity, bottom_capacity):
    return new_upperdeck_capacity + bottom_capacity

def main():
    user_input = get_user_input()
    (max_height, max_width, max_draft, max_length, s_width, s_total_height, s_length, s_draft, container_width, container_length, capacity, prismatic_co) = user_input

    bottom_capacity = find_container_bottom_TEU(s_width, s_total_height, s_length, container_width, container_length, capacity, prismatic_co)
    upper_estimate = find_container_upper_TEU(bottom_capacity)
    upper_height = find_upper_height(upper_estimate, s_length, container_length, s_width, container_width)
    center_of_gravity = find_center_of_gravity(s_width, s_total_height, s_length, upper_height)
    center_of_buoyancy = find_center_of_buoyancy(s_draft)
    moment_of_inertia = find_moment_of_inertia(s_width, s_length)
    metacentric_height = find_metacentric_height(center_of_buoyancy, center_of_gravity, moment_of_inertia, s_draft, s_width, s_length)

    stability_result = stability_check(metacentric_height, s_width, s_length, s_draft, upper_height, center_of_buoyancy, moment_of_inertia, max_width, max_length, max_draft, s_total_height)
    final_upper_capacity = new_upperdeck_capacity(upper_estimate, stability_result[4])
    total_capacity = find_full_capacity(final_upper_capacity, bottom_capacity)

    print("\nResults:")
    print(f"Bottom Deck Capacity: {bottom_capacity} containers")
    print(f"Projected Upper Deck Capacity: {upper_estimate} containers")
    print(f"Final Upper Deck Capacity: {final_upper_capacity} containers")
    print(f"Total Ship Capacity: {total_capacity} containers")
    print(f"Final Metacentric Height (GM): {stability_result[0]:.2f} meters")

if __name__ == "__main__":
    main()
